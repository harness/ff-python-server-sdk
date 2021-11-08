=======================
Feature Flag Server SDK
=======================

.. image:: https://img.shields.io/pypi/v/harness-featureflags.svg
        :target: https://pypi.python.org/pypi/harness-featureflags

.. image:: https://readthedocs.org/projects/ff-python-server-sdk/badge/?version=latest
        :target: https://ff-python-server-sdk.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/drone/ff_python_server_sdk/shield.svg
     :target: https://pyup.io/repos/github/drone/ff_python_server_sdk/
     :alt: Updates

Overview
--------

+---------------------------+
| `Harness <https://www.har |
| ness.io/>`__              |
| is a feature management   |
| platform that helps teams |
| to build better software  |
| and to test features      |
| quicker.                  |
+---------------------------+

Setup
-----

using terminal install lib with:

::

        pip install harness-featureflags

After package has been added, the SDK elements, primarily ``CfClient``
should be accessible in the main application.

Initialization
--------------

``CfClient`` is a base class that provides all features of SDK.

::

        """
        Put the API Key here from your environment
        """
        api_key = "YOUR_API_KEY";

        cf = CfClient(api_key);

        """
        Define you target on which you would like to evaluate
        the featureFlag
        """
        target = Target(identifier="user1")
        target = Target(name="User1")

``target`` represents the desired target for which we want features to
be evaluated.

``"YOUR_API_KEY"`` is an authentication key, needed for access to
Harness services.

**Your Harness SDK is now initialized. Congratulations!**

Public API Methods
~~~~~~~~~~~~~~~~~~

The Public API exposes a few methods that you can utilize:

-  ``bool_variation(key: str, target: Target, default: bool) -> bool``

-  ``string_variation(key: str, target: Target, default: str) -> str``

-  ``number_variation(key: str, target: Target, default: float) -> float``

-  ``json_variation(String key, Target target, default: dict) -> dict``

-  ``close()``

Fetch evaluation's value
------------------------

It is possible to fetch a value for a given evaluation. Evaluation is
performed based on a different type. In case there is no evaluation with
provided id, the default value is returned.

Use the appropriate method to fetch the desired Evaluation of a certain
type.

Bool variation
~~~~~~~~~~~~~~

::

        result = cf.bool_variation("sample_boolean_flag", target, False);

Number variation
~~~~~~~~~~~~~~~~

::

        result = cf.number_variation("sample_number_flag", target, 0);

String variation
~~~~~~~~~~~~~~~~

::

        result = cf.string_variation("sample_string_flag", target, "");

Using feature flags metrics
---------------------------

Metrics API endpoint can be changed like this:

::

        cf = CfClient(api_key, with_events_url('METRICS_API_EVENTS_URL'));

Otherwise, the default metrics endpoint URL will be used.

Shutting down the SDK
---------------------

To avoid potential memory leak, when SDK is no longer needed (when the
app is closed, for example), a caller should call this method:

::

        cf.close();

