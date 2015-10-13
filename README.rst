django-flexy
============

``django-flexy`` hooks up Django with Elasticsearch.

By itself, it is just a thin wrapper on top of `elasticsearch-dsl`_.

Configuration
-------------

Add ``flexy`` to your ``INSTALLED_APPS``::

  INSTALLED_APPS = (
      ...
      'flexy',
      ...
  )


Then you must configure *connections*, *indexes* and *indexers*.

Connections are connections to Elasticsearch instances,
of which you can have more than one.

Like database connections in Django,
they are named and the one called ``default`` is mandatory.

They are configured via the ``FLEXY_CONNECTIONS`` setting, like this::

  FLEXY_CONNECTIONS = {
      'default': {
          'hosts': 'localhost'
      },
      # Optional additional connections
      # 'special_conn': {
      #     'hosts': ['localhost', '192.168.1.121:9200']
      # }
  }

See `elasticsearch-dsl connections`_ for more info.

Indexes are all the different buckets where your data ends up,
somewhat similar to SQL tables, and they might have a schema.

Note that having a schema doesn't mean
it is not possible to index other things
in addition to what is in the schema:
this is totally possible and also the default setting of Elasticsearch.

In order to define multiple indexes you populate the ``FLEXY_INDEXES`` setting::

  FLEXY_INDEXES = {
      'main': {  # Index name
          'connection': 'default',  # See connections above
          'settings': {
              # Optional Elasticsearch index settings here, see
              # https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html#create-index-settings
          },
          'mappings': {
              # See https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
              # and https://www.elastic.co/guide/en/elasticsearch/guide/current/custom-dynamic-mapping.html
              'foo_type': {
                  'dynamic_templates': [
                      {
                          'plain_strings': {
                              'match': '*_string',
                              'match_mapping_type': 'string',
                              'mapping': {
                                  'type': 'string',
                                  'index': 'not_analyzed'
                              }
                          }
                      }
                  ],
                  'properties': {
                      'foo': {
                          'type': 'string',
                          'index': 'not_analyzed'
                      }
                  }
              }
          }
      }
  }


Now Elasticsearch just needs to know how to populate the data
(how to index your models) and to do that one uses *indexers*,
whch are configured through the setting ``FLEXY_INDEXERS``::

  FLEXY_INDEXERS = {
      'appname.foo': {
          'index': 'main',
          'type': 'foo',
          'data': {'foo': 'fieldname'}
      },
      'appname.bar': 'appname.indexers.bar'
  }

This warrants a bit of explanation:

 * Every key is the dictionary is a model identifier
   (``<app_label>.<model_name>``)
 * The value can be either a mapping or a string
 * If it is a mapping, it must contain three keys:
   ``index``, whose value is the index where this model is stored;
   ``type``, which is the document type that it has
   (see mappings above,
   the document type is the keys under the ``mappings`` key of the index);
   and ``data`` which is a dictionary
   where for every field in the index we have the corresponding field
   on the model (one-to-one)
 * If it is a string, it must be the dotted name of a function that,
   if invoked with the ``instance`` (i.e. model to be indexed)
   as a single argument,
   returns a dictionary with the same keys as before
   (``index``, ``type``, ``data``)
   but where data has the actual values to index
   (not string containing attribute names)

It is recommended to use the second form of indexer (function)
for everything but the most trivial needs.

Once all this is set up, ``django-flexy`` registers a signal handler that,
upon model saving, indexes the model (if it is cited in ``FLEXY_INDEXERS``).

Searching
---------

Searching is done exactly as with `elasticsearch-dsl search`_.

It is worth noting that connections defined in ``FLEXY_CONNECTIONS``
are lazily registered with `elasticsearch-dsl`_,
so if you have a basic search you can just do::

  Search().query(...).execute()

Or if you want to use the connection ``special_conn`` just do::

  Search('special_conn').query(...).execute()

The major ptoblem you have here is that the results
do not allow you to easily get to the model
(should the data stored in elastic prove insufficient).

For this you have the utility methods
``load_instance`` and ``load_instances`` in ``flexy.results``::

  from flexy.results import load_instance, load_instances

  results = Search().query(...).execute()
  load_instance(results.hits[0])      # For a single result
  load_instances(results.hits[0:30])  # Optimized for lists and the like

The main difference between the two is that ``load_instances``
operates on an iterable of results (lists, tuple, whatever)
and minimizes the queries sent to the database.

It still isn't extremely efficient,
so it is better if you use it on small data sets (< 200).

Commands
--------

``django-flexy`` comes with two useful management commands::

``sync_elastic``
    Creates the indexes and updates them if their settings have changed.
    It's a bit like ``syncdb``, but for elastic.

``reindex``
    Reindexes content. Useful after imports and the like.


.. _`elasticsearch-dsl`: https://elasticsearch-dsl.readthedocs.org/en/latest/
.. _`elasticsearch-dsl connections`: https://elasticsearch-dsl.readthedocs.org/en/latest/configuration.html
.. _`elasticsearch-dsl search`: https://elasticsearch-dsl.readthedocs.org/en/latest/search_dsl.html
