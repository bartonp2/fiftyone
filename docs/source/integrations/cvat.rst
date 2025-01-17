.. _cvat-integration:

CVAT Integration
================

.. default-role:: code

`CVAT <https://github.com/openvinotoolkit/cvat>`_ is one of the most popular
open-source image and video annotation tools available, and we've made it easy
to upload your data directly from FiftyOne to CVAT to add or edit labels.

You can use CVAT either through the demo server at
`cvat.org <https://cvat.org>`_ or through a
`self-hosted server <https://openvinotoolkit.github.io/cvat/docs/administration/basics/installation/>`_.
In either case, FiftyOne provides :ref:`simple setup <cvat-setup>` instructions
that you can use to specify the necessary account credentials and server
endpoint to use.

CVAT provides three levels of abstraction for annotation workflows: projects,
tasks, and jobs. A job contains one or more images and can be assigned to a
specfic annotator or reviewer. A task defines the label schema to use for
annotation and contains one or more jobs. A project can optionally be created
to group multiple tasks together under a shared label schema.

FiftyOne provides an API to create tasks and jobs, upload data, define label
schemas, and download annotations using CVAT, all programmatically in Python.
All of the following label types are supported, for both image and video
datasets:

- :ref:`Classifications <classification>`
- :ref:`Detections <object-detection>`
- :ref:`Instance segmentations <instance-segmentation>`
- :ref:`Polygons and polylines <polylines>`
- :ref:`Keypoints <keypoints>`
- :ref:`Scalar fields <adding-sample-fields>`

.. image:: /images/integrations/cvat_example.png
   :alt: cvat-example
   :align: center

.. note::

    Check out :doc:`this tutorial </tutorials/cvat_annotation>` to see how
    you can use FiftyOne to upload your data to CVAT to create, delete, and fix
    annotations.

.. _cvat-basic-recipe:

Basic recipe
____________

The basic workflow to use CVAT to add or edit labels on your FiftyOne datasets
is as follows:

1) Load a :ref:`labeled or unlabeled dataset <loading-datasets>` into FiftyOne

2) Explore the dataset using the :ref:`App <fiftyone-app>` or
   :ref:`dataset views <using-views>` to locate either unlabeled samples that
   you wish to annotate or labeled samples whose annotations you want to edit

3) Use the
   :meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`
   method on your dataset or view to upload the samples and optionally their
   existing labels to CVAT

4) In CVAT, perform the necessary annotation work

5) Back in FiftyOne, load your dataset and use the
   :meth:`load_annotations() <fiftyone.core.collections.SampleCollection.load_annotations>`
   method to merge the annotations back into your FiftyOne dataset

6) If desired, delete the CVAT tasks and the record of the annotation run from
   your FiftyOne dataset

|br|
The example below demonstrates this workflow.

.. note::

    You must create an account at `cvat.org <https://cvat.org>`_ in order to
    run this example.

    Note that you can store your credentials as described in
    :ref:`this section <cvat-setup>` to avoid entering them manually each time
    you interact with CVAT.

First, we create the annotation tasks in CVAT:

.. code-block:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz
    from fiftyone import ViewField as F

    # Step 1: Load your data into FiftyOne

    dataset = foz.load_zoo_dataset(
        "quickstart", dataset_name="cvat-annotation-example"
    )
    dataset.persistent = True

    dataset.evaluate_detections(
        "predictions", gt_field="ground_truth", eval_key="eval"
    )

    # Step 2: Locate a subset of your data requiring annotation

    # Create a view that contains only high confidence false positive model
    # predictions, with samples containing the most false positives first
    most_fp_view = (
        dataset
        .filter_labels("predictions", (F("confidence") > 0.8) & (F("eval") == "fp"))
        .sort_by(F("predictions.detections").length(), reverse=True)
    )

    # Let's edit the ground truth annotations for the sample with the most
    # high confidence false positives
    sample_id = most_fp_view.first().id
    view = dataset.select(sample_id)

    # Step 3: Send samples to CVAT

    # A unique identifier for this run
    anno_key = "cvat_basic_recipe"

    view.annotate(
        anno_key,
        label_field="ground_truth",
        attributes=["iscrowd"],
        launch_editor=True,
    )
    print(dataset.get_annotation_info(anno_key))

    # Step 4: Perform annotation in CVAT and save the tasks

Then, once the annotation work is complete, we merge the annotations back into
FiftyOne:

.. code-block:: python
    :linenos:

    import fiftyone as fo

    anno_key = "cvat_basic_recipe"

    # Step 5: Merge annotations back into FiftyOne dataset

    dataset = fo.load_dataset("cvat-annotation-example")
    dataset.load_annotations(anno_key)

    # Load the view that was annotated in the App
    view = dataset.load_annotation_view(anno_key)
    session = fo.launch_app(view=view)

    # Step 6: Cleanup

    # Delete tasks from CVAT
    results = dataset.load_annotation_results(anno_key)
    results.cleanup()

    # Delete run record (not the labels) from FiftyOne
    dataset.delete_annotation_run(anno_key)

.. note::

    Skip to :ref:`this section <cvat-examples>` to see a variety of common CVAT
    annotation patterns.

.. _cvat-setup:

Setup
_____

FiftyOne supports both `cvat.org <https://cvat.org>`_ and
`self-hosted servers <https://openvinotoolkit.github.io/cvat/docs/administration/basics/installation/>`_.

The easiest way to get started is to use the default server
`cvat.org <https://cvat.org>`_, which simply requires creating an account and
then providing your authentication credentials as shown below.

Authentication
--------------

In order to connect to a CVAT server, you must provide your login credentials,
which can be done in a variety of ways.

**Environment variables (recommended)**

The recommended way to configure your CVAT login credentials is to store them
in the `FIFTYONE_CVAT_USERNAME` and `FIFTYONE_CVAT_PASSWORD` environment
variables. These are automatically accessed by FiftyOne whenever a connection
to CVAT is made.

.. code-block:: shell

    export FIFTYONE_CVAT_USERNAME=...
    export FIFTYONE_CVAT_PASSWORD=...

**FiftyOne annotation config**

You can also store your credentials in your
:ref:`annotation config <annotation-config>` located at
`~/.fiftyone/annotation_config.json`:

.. code-block:: text

    {
        "backends": {
            "cvat": {
                "username": ...,
                "password": ...
            }
        }
    }

Note that this file will not exist until you create it.

.. warning::

    Storing your username and password in plain text on disk is generally not
    recommended. Consider using environment variables instead.

**Keyword arguments**

You can manually provide your login credentials as keyword arguments each time
you call methods like
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>` and
:meth:`load_annotations() <fiftyone.core.collections.SampleCollection.load_annotations>`
that require connections to CVAT:

.. code:: python
    :linenos:

    view.annotate(
        anno_key,
        label_field="ground_truth",
        username=...,
        password=...,
    )

**Command line prompt**

If you have not stored your login credentials via another method, you will be
prompted to enter them interactively in your shell each time you call a method
that requires a connection to CVAT:

.. code:: python
    :linenos:

    view.annotate(anno_key, label_field="ground_truth", launch_editor=True)

.. code-block:: text

    Please enter your login credentials.
    You can avoid this in the future by setting your `FIFTYONE_CVAT_USERNAME` and `FIFTYONE_CVAT_PASSWORD` environment variables.
    Username: ...
    Password: ...

.. _cvat-self-hosted-server:

Self-hosted servers
-------------------

If you wish to use a
`self-hosted server <https://openvinotoolkit.github.io/cvat/docs/administration/basics/installation/>`_,
you can configure the URL of your server in any of the following ways:

-   Set the `FIFTYONE_CVAT_URL` environment variable:

.. code-block:: shell

    export FIFTYONE_CVAT_URL=http://localhost:8080

-   Store the `url` of your server in your
    :ref:`annotation config <annotation-config>` at
    `~/.fiftyone/annotation_config.json`:

.. code-block:: text

    {
        "backends": {
            "cvat": {
                "url": "http://localhost:8080"
            }
        }
    }

-   Pass the `url` parameter manually each time you call
    :meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`:

.. code:: python
    :linenos:

    view.annotate(
        anno_key,
        label_field="ground_truth",
        url="http://localhost:8080",
        username=...,
        password=...,
    )

.. _cvat-requesting-annotations:

Requesting annotations
______________________

Use the
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>` method
to send the samples and optionally existing labels in a |Dataset| or
|DatasetView| to CVAT for annotation.

The basic syntax is:

.. code:: python
    :linenos:

    anno_key = "..."
    view.annotate(anno_key, ...)

The `anno_key` argument defines a unique identifier for the annotation run, and
you will provide it to methods like
:meth:`load_annotations() <fiftyone.core.collections.SampleCollection.load_annotations>`,
:meth:`get_annotation_info() <fiftyone.core.collections.SampleCollection.load_annotations>`,
:meth:`load_annotation_results() <fiftyone.core.collections.SampleCollection.load_annotation_results>`, and
:meth:`delete_annotation_run() <fiftyone.core.collections.SampleCollection.delete_annotation_run>`
to manage the run in the future.

.. note::

    Calling
    :meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`
    will upload the source media files to the CVAT server.

In addition,
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`
provides various parameters that you can use to customize the annotation tasks
that you wish to be performed.

The following parameters are supported by all annotation backends:

-   **backend** (*None*): the annotation backend to use. Use `"cvat"` for the
    CVAT backend. The supported values are
    `fiftyone.annotation_config.backends.keys()` and the default is
    `fiftyone.annotation_config.default_backend`
-   **media_field** (*"filepath"*): the sample field containing the path to the
    source media to upload
-   **launch_editor** (*False*): whether to launch the annotation backend's
    editor after uploading the samples

The following parameters allow you to configure the labeling schema to use for
your annotation tasks. See :ref:`this section <cvat-label-schema>` for more
details:

-   **label_schema** (*None*): a dictionary defining the label schema to use.
    If this argument is provided, it takes precedence over `label_field` and
    `label_type`
-   **label_field** (*None*): a string indicating a new or existing label field
    to annotate
-   **label_type** (*None*): a string or type indicating the type of labels to
    annotate. The possible label strings/types are:

    -   `"classification"`: :class:`fiftyone.core.labels.Classification`
    -   `"classifications"`: :class:`fiftyone.core.labels.Classifications`
    -   `"detection"`: :class:`fiftyone.core.labels.Detection`
    -   `"detections"`: :class:`fiftyone.core.labels.Detections`
    -   `"polyline"`: :class:`fiftyone.core.labels.Polyline`
    -   `"polylines"`: :class:`fiftyone.core.labels.Polylines`
    -   `"keypoint"`: :class:`fiftyone.core.labels.Keypoint`
    -   `"keypoints"`: :class:`fiftyone.core.labels.Keypoints`

    You can also specify `"scalar"` for a primitive scalar field or pass any of
    the supported scalar field types:

    -   :class:`fiftyone.core.fields.IntField`
    -   :class:`fiftyone.core.fields.FloatField`
    -   :class:`fiftyone.core.fields.StringField`
    -   :class:`fiftyone.core.fields.BooleanField`

    All new label fields must have their type specified via this argument or in
    `label_schema`
-   **classes** (*None*): a list of strings indicating the class options for
    `label_field` or all fields in `label_schema` without classes specified.
    All new label fields must have a class list provided via one of the
    supported methods. For existing label fields, if classes are not provided
    by this argument nor `label_schema`, they are parsed from
    :meth:`Dataset.classes <fiftyone.core.dataset.Dataset.classes>` or
    :meth:`Dataset.default_classes <fiftyone.core.dataset.Dataset.default_classes>`
-   **attributes** (*True*): specifies the label attributes of each label field
    to include (other than their `label`, which is always included) in the
    annotation export. Can be any of the following:

    -   `True`: export all label attributes
    -   `False`: don't export any custom label attributes
    -   a list of label attributes to export
    -   a dict mapping attribute names to dicts specifying the `type`,
        `values`, and `default` for each attribute

In addition, the following CVAT-specific parameters from
:class:`CVATBackendConfig <fiftyone.utils.cvat.CVATBackendConfig>` can also be
provided:

-   **segment_size** (*None*): the maximum number of images to upload per job.
    Not applicable to videos
-   **image_quality** (*75*): an int in `[0, 100]` determining the image
    quality to upload to CVAT
-   **task_assignee** (*None*): a username to assign the generated tasks
-   **job_assignees** (*None*): a list of usernames to assign jobs
-   **job_reviewers** (*None*): a list of usernames to assign job reviews

.. _cvat-label-schema:

Label schema
------------

The `label_schema`, `label_field`, `label_type`, `classes`, and `attributes`
parameters to
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>` allow
you to define the annotation schema that you wish to be used.

The label schema may define new label field(s) that you wish to populate, and
it may also include existing label field(s), in which case you can add, delete,
or edit the existing labels on your FiftyOne dataset.

The `label_schema` argument is the most flexible way to define how to construct
tasks in CVAT. In its most verbose form, it is a dictionary that defines the
label type, annotation type, possible classes, and possible attributes for each
label field:

.. code:: python
    :linenos:

    anno_key = "..."

    label_schema = {
        "new_field": {
            "type": "classifications",
            "classes": ["class1", "class2"],
            "attributes": {
                "attr1": {
                    "type": "select",
                    "values": ["val1", "val2"],
                    "default": "val1",
                },
                "attr2": {
                    "type": "radio",
                    "values": [True, False],
                    "default": False,
                }
            },
        },
        "existing_field": {
            "classes": ["class3", "class4"],
            "attributes": {
                "attr3": {
                    "type": "text",
                }
            }
        },
    }

    dataset.annotate(anno_key, label_schema=label_schema)

Alternatively, if you are only editing or creating a single label field, you
can use the `label_field`, `label_type`, `classes`, and `attributes` parameters
to specify the components of the label schema individually:

.. code:: python
    :linenos:

    anno_key = "..."

    label_field = "new_field",
    label_type = "classifications"
    classes = ["class1", "class2"]

    # These are optional
    attributes = {
        "attr1": {
            "type": "select",
            "values": ["val1", "val2"],
            "default": "val1",
        },
        "attr2": {
            "type": "radio",
            "values": [True, False],
            "default": False,
        }
    }

    dataset.annotate(
        anno_key,
        label_field=label_field,
        label_type=label_type,
        classes=classes,
        attributes=attributes,
    )

When you are annotating existing label fields, you can omit some of these
parameters from
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`, as
FiftyOne can infer the appropriate values to use:

-   **label_type**: if omitted, the |Label| type of the field will be used to
    infer the appropriate value for this parameter
-   **classes**: if omitted, the class lists from the
    :meth:`classes <fiftyone.core.dataset.Dataset.classes>` or
    :meth:`default_classes <fiftyone.core.dataset.Dataset.default_classes>`
    properties of your dataset will be used, if available. Otherwise, the
    observed labels on your dataset will be used to construct a classes list

.. _cvat-label-attributes:

Label attributes
----------------

The `attributes` parameter allows you to configure whether
:ref:`custom attributes <label-attributes>` beyond the default `label`
attribute are included in the annotation tasks.

When adding new label fields for which you want to include attributes, you must
use the dictionary syntax demonstrated below to define the schema of each
attribute that you wish to label:

.. code:: python
    :linenos:

    anno_key = "..."

    attributes = {
        "occluded": {
            "type": "radio",
            "values": [True, False],
            "default": True,
        },
        "weather": {
            "type": "select",
            "values": ["cloudy", "sunny", "overcast"],
        },
        "caption": {
            "type": "text",
        }
    }

    view.annotate(
        anno_key,
        label_field="new_field",
        label_type="detections",
        classes=["dog", "cat", "person"],
        attributes=attributes,
    )

You can always omit this parameter if you do not require attributes beyond the
default `label`.

For CVAT, the following `type` values are supported:

-   `text`: a free-form text box. In this case, `default` is optional and
    `values` is unused
-   `select`: a selection dropdown. In this case, `values` is required and
    `default` is optional
-   `radio`: a radio button list UI. In this case, `values` is required and
    `default` is optional
-   `checkbox`: a boolean checkbox UI. In this case, `default` is optional and
    `values` is unused

When you are annotating existing label fields, the `attributes` parameter can
take additional values:

-   `True` (default): export all custom attributes observed on the existing
    labels, using their observed values to determine the appropriate UI type
    and possible values, if applicable
-   `False`: do not include any custom attributes in the export
-   a list of custom attributes to include in the export
-   a full dictionary syntax described above

.. note::

    Only scalar-valued label attributes are supported. Other attribute types
    like lists, dictionaries, and arrays will be omitted.

.. note::

    When uploading existing labels to CVAT, their label IDs in FiftyOne are
    always uploaded as attributes. This information is used to keep track of
    modifications to existing labels, and changing or deleting these ID
    attributes in CVAT will result in labels being overwritten rather than
    merged when loading annotations back into FiftyOne.

.. _cvat-loading-annotations:

Loading annotations
___________________

After your annotations tasks in the annotation backend are complete, you can
use the
:meth:`load_annotations() <fiftyone.core.collections.SampleCollection.load_annotations>`
method to download them and merge them back into your FiftyOne dataset.

.. code:: python
    :linenos:

    view.load_annotations(anno_key)

The `anno_key` parameter is the unique identifier for the annotation run that
you provided when calling
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`. You
can use
:meth:`list_annotation_runs() <fiftyone.core.collections.SampleCollection.list_annotation_runs>`
to see the available keys on a dataset.

.. note::

    By default, calling
    :meth:`load_annotations() <fiftyone.core.collections.SampleCollection.load_annotations>`
    will not delete any information for the run from the annotation backend.

    However, you can pass `cleanup=True` to delete all information associated
    with the run from the backend after the annotations are downloaded.

.. _cvat-managing-annotation-runs:

Managing annotation runs
________________________

FiftyOne provides a variety of methods that you can use to manage in-progress
or completed annotation runs.

For example, you can call
:meth:`list_annotation_runs() <fiftyone.core.collections.SampleCollection.list_annotation_runs>`
to see the available annotation keys on a dataset:

.. code:: python
    :linenos:

    dataset.list_annotation_runs()

Or, you can use
:meth:`get_annotation_info() <fiftyone.core.collections.SampleCollection.get_annotation_info>`
to retrieve information about the configuration of an annotation run:

.. code:: python
    :linenos:

    info = dataset.get_annotation_info(anno_key)
    print(info)

Use :meth:`load_annotation_results() <fiftyone.core.collections.SampleCollection.load_annotation_results>`
to load the :class:`AnnotationResults <fiftyone.utils.annotations.AnnotationResults>`
instance for an annotation run.

All results objects provide a :class:`cleanup() <fiftyone.utils.annotations.AnnotationResults.cleanup>`
method that you can use to delete all information associated with a run from
the annotation backend.

.. code:: python
    :linenos:

    results = dataset.load_annotation_results(anno_key)
    results.cleanup()

In addition, the
:class:`AnnotationResults <fiftyone.utils.annotations.AnnotationResults>`
subclasses for each backend may provide additional utilities such as support
for programmatically monitoring the status of the annotation tasks in the run.

Finally, you can use
:meth:`delete_annotation_run() <fiftyone.core.collections.SampleCollection.delete_annotation_run>`
to delete the record of an annotation run from your FiftyOne dataset:

.. code:: python
    :linenos:

    dataset.delete_annotation_run(anno_key)

.. note::

    Calling
    :meth:`delete_annotation_run() <fiftyone.core.collections.SampleCollection.delete_annotation_run>`
    only deletes the **record** of the annotation run from your FiftyOne
    dataset; it will not delete any annotations loaded onto your dataset via
    :meth:`load_annotations() <fiftyone.core.collections.SampleCollection.load_annotations>`,
    nor will it delete any associated information from the annotation backend.

.. _cvat-examples:

Examples
________

This section demonstrates how to perform some common annotation workflows on a
FiftyOne dataset using the CVAT backend.

.. note::

    All of the examples below assume you have configured your CVAT server and
    credentials as described in :ref:`this section <cvat-setup>`.

Modifying an existing label field
---------------------------------

A common use case is to fix annotation mistakes that you discovered in your
datasets through FiftyOne.

You can easily edit the labels in an existing field of your FiftyOne dataset
by simply passing the name of the field via the `label_field` parameter of
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_existing_field"

    view.annotate(anno_key, label_field="ground_truth", launch_editor=True)
    print(dataset.get_annotation_info(anno_key))

    # Modify/add/delete bounding boxes and their attributes in CVAT

    dataset.load_annotations(anno_key, cleanup=True)
    dataset.delete_annotation_run(anno_key)

.. image:: /images/integrations/cvat_example.png
   :alt: cvat-example
   :align: center

|br|
The above code snippet will infer the possible classes and label attributes
from your FiftyOne dataset. However, the `classes` and `attributes` parameters
can be used to annotate new classes and/or attributes:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_existing_field"

    # The list of possible `label` values
    classes = ["person", "dog", "cat", "helicopter"]

    # Details for the existing `iscrowd` attribute are automatically inferred
    # A new `attr2` attribute is also added
    attributes = {
        "iscrowd": {},
        "attr2": {
            "type": "select",
            "values": ["val1", "val2"],
        }
    }

    view.annotate(
        anno_key,
        label_field="ground_truth",
        classes=classes,
        attributes=attributes,
        launch_editor=True,
    )
    print(dataset.get_annotation_info(anno_key))

    # Modify/add/delete bounding boxes and their attributes in CVAT

    dataset.load_annotations(anno_key, cleanup=True)
    dataset.delete_annotation_run(anno_key)

.. image:: /images/integrations/cvat_new_class.png
   :alt: cvat-new-class
   :align: center

.. note::

    When uploading existing labels to CVAT, the label IDs are uploaded as
    attributes. This information is used to keep track of which labels have
    been modified, added, or deleted, and thus editing these label IDs will
    result in labels being overwritten when
    loaded into FiftyOne rather than being merged.

Adding new label fields
-----------------------

In order to annotate a new label field, you can provide the `label_field`,
`label_type`, and `classes` parameters to
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>` to
define the annotation schema for the field:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_new_field"

    view.annotate(
        anno_key,
        label_field="new_classifications",
        label_type="classifications",
        classes=["dog", "cat", "person"],
        launch_editor=True,
    )
    print(dataset.get_annotation_info(anno_key))

    # Create annotations in CVAT

    dataset.load_annotations(anno_key, cleanup=True)
    dataset.delete_annotation_run(anno_key)

Alternatively, you can use the `label_schema` argument to define the same
labeling task:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_new_field"

    label_schema = {
        "new_classifications": {
            "type": "classifications",
            "classes": ["dog", "cat", "person"],
        }
    }

    view.annotate(anno_key, label_schema=label_schema, launch_editor=True)
    print(dataset.get_annotation_info(anno_key))

    # Create annotations in CVAT

    dataset.load_annotations(anno_key, cleanup=True)
    dataset.delete_annotation_run(anno_key)

.. image:: /images/integrations/cvat_tag.png
   :alt: cvat-tag
   :align: center

Annotating multiple fields
--------------------------

The `label_schema` argument allows you to define annotation tasks for multiple
fields at once:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_multiple_fields"

    # The details for existing `ground_truth` field are inferred
    # A new field `new_keypoints` is also added
    label_schema = {
        "ground_truth": {},
        "new_keypoints": {
            "type": "keypoints",
            "classes": ["person", "cat", "dog", "food"],
            "attributes": {
                "occluded": {
                    "type": "select",
                    "values": [True, False],
                }
            }
        }
    }

    view.annotate(anno_key, label_schema=label_schema, launch_editor=True)
    print(dataset.get_annotation_info(anno_key))

    # Add annotations in both CVAT tasks that were created

    dataset.load_annotations(anno_key, cleanup=True)
    dataset.delete_annotation_run(anno_key)

.. note:

    When annotating multiple fields, each field will get its own CVAT task.

.. image:: /images/integrations/cvat_multiple_fields.png
   :alt: cvat-multiple-fields
   :align: center

Unexpected annotations
----------------------

The :meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`
method allows you to define the annotation schema that should be followed in
CVAT. However, you or your annotators may "violate" this schema by adding
annotations whose types differ from the pre-configured tasks.

For example, suppose you upload a |Detections| field to CVAT for editing, but
then polyline annotations are added instead. In such cases, the
:meth:`load_annotations() <fiftyone.core.collections.SampleCollection.load_annotations>`
method will present a command prompt asking you what field(s) (if any) to store
these unexpected new labels in:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_unexpected"

    view.annotate(anno_key, label_field="ground_truth", launch_editor=True)
    print(dataset.get_annotation_info(anno_key))

    # Add some polyline annotations in CVAT (wrong type!)

    # You will be prompted for a field in which to store the polylines
    dataset.load_annotations(anno_key, cleanup=True)
    dataset.delete_annotation_run(anno_key)

.. image:: /images/integrations/cvat_polyline.png
   :alt: cvat-polyline
   :align: center

Assigning users
---------------

When using the CVAT backend, you can provide the following optional parameters
to :meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>` to
specify which users will be assigned to the created tasks:

-   `segment_size`: the maximum number of images to include in a single job
-   `task_assignee`: a username to assign the generated tasks
-   `job_assignees`: a list of usernames to assign jobs
-   `job_reviewers`: a list of usernames to assign job reviews

If the number of jobs exceeds the number of assignees or reviewers, the jobs
will be assigned using a round-robin strategy.

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(5)

    anno_key = "cvat_assign_users"

    task_assignee = "username1"
    job_assignees = ["username2", "username3"]
    job_reviewers = ["username4", "username5", "username6", "username7"]

    # Load "ground_truth" field into one task
    # Create another task for "keypoints" field
    label_schema = {
        "ground_truth": {},
        "keypoints": {
            "type": "keypoints",
            "classes": ["person"],
        }
    }

    view.annotate(
        anno_key,
        label_schema=label_schema,
        segment_size=2,
        task_assignee=task_assignee,
        job_assignees=job_assignees,
        job_reviewers=job_reviewers,
        launch_editor=True,
    )
    print(dataset.get_annotation_info(anno_key))

    # Cleanup
    results = dataset.load_annotation_results(anno_key)
    results.cleanup()
    dataset.delete_annotation_run(anno_key)

Scalar labels
-------------

|Label| fields are the preferred way to store information for common tasks
such as classification and detection in your FiftyOne datasets. However, you
can also store CVAT annotations in scalar fields of type `float`, `int`, `str`,
or  `bool` .

When storing annotations in scalar fields, the `label_field` parameter is still
used to define the name of the field, but the `classes` argument is now
optional and the `attributes` argument is unused.

If `classes` are provided, you will be able to select from these values in
CVAT; otherwise, the CVAT tag will show the `label_field` name and you must
enter the appropriate scalar in the `value` attribute of the tag.

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_scalar_fields"

    # Create two scalar fields, one with classes and one without
    label_schema = {
        "scalar1": {
            "type": "scalar",
        },
        "scalar2": {
            "type": "scalar",
            "classes": ["class1", "class2", "class3"],
        }
    }

    view.annotate(anno_key, label_schema=label_schema, launch_editor=True)
    print(dataset.get_annotation_info(anno_key))

    # Cleanup
    results = dataset.load_annotation_results(anno_key)
    results.cleanup()
    dataset.delete_annotation_run(anno_key)

.. image:: /images/integrations/cvat_scalar.png
   :alt: cvat-scalar
   :align: center

Uploading alternate media
-------------------------

In some cases, you may want to upload media files other than those stored in
the `filepath` field of your dataset's samples for annotation. For example,
you may have a dataset with personal information like faces or license plates
that must be anonymized before uploading for annotation.

The recommended approach in this case is to store the alternative media files
for each sample on disk and record these paths in a new field of your FiftyOne
dataset. You can then specify this field via the `media_field` parameter of
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`.

For example, let's upload some blurred images to CVAT for annotation:

.. code:: python
    :linenos:

    import os
    import cv2

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_alt_media"

    alt_dir = "/tmp/blurred"
    if not os.path.exists(alt_dir):
        os.makedirs(alt_dir)

    # Blur images
    for sample in view:
        filepath = sample.filepath
        alt_filepath = os.path.join(alt_dir, os.path.basename(filepath))

        img = cv2.imread(filepath)
        cv2.imwrite(alt_filepath, cv2.blur(img, (20, 20)))

        sample["alt_filepath"] = alt_filepath
        sample.save()

    view.annotate(
        anno_key,
        label_field="ground_truth",
        media_field="alt_filepath",
        launch_editor=True,
    )
    print(dataset.get_annotation_info(anno_key))

    # Create annotations in CVAT

    dataset.load_annotations(anno_key, cleanup=True)
    dataset.delete_annotation_run(anno_key)

.. image:: /images/integrations/cvat_alt_media.png
   :alt: cvat-alt-media
   :align: center

.. _cvat-annotating-videos:

Annotating videos
_________________

You can add or edit annotations for video datasets using the CVAT backend
through the
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`
method.

All CVAT label types except `tags` provide an option to annotate **tracks** in
videos, which captures the identity of a single object as it moves through the
video. These tracks are stored in the `index` field of the |Label| instances
when you import the annotations into FiftyOne.

Note that CVAT does not provide a straightforward way to annotate frame-level
classification labels. Instead, we recommend that you use sample-level fields
to record classifications for your video datasets.

.. note::

    Prepend `"frames."` to reference frame-level fields when calling
    :meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`.

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart-video")
    view = dataset.take(1)

    anno_key = "cvat_video"

    # Send frame-level detections to CVAT
    view.annotate(
        anno_key,
        label_field="frames.detections",
        launch_editor=True,
    )
    print(dataset.get_annotation_info(anno_key))

    # Edit annotations in CVAT...

    # Merge edits back in
    dataset.load_annotations(anno_key)

    # Load the view that was annotated in the App
    view = dataset.load_annotation_view(anno_key)
    session = fo.launch_app(view=view)

    # Cleanup
    results = dataset.load_annotation_results(anno_key)
    results.cleanup()
    dataset.delete_annotation_run(anno_key)

.. note:

    CVAT only allows one video per task, so calling
    :meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>`
    on a video dataset will result multiple tasks per label field.

.. image:: /images/integrations/cvat_video.png
   :alt: cvat-video
   :align: center

.. _cvat-utils:

Additional utilities
____________________

You can perform additional CVAT-specific operations to monitor the progress
of an annotation task initiated by
:meth:`annotate() <fiftyone.core.collections.SampleCollection.annotate>` via
the returned
:class:`CVATAnnotationResults <fiftyone.utils.cvat.CVATAnnotationResults>`
instance.

The sections below highlight some common actions that you may want to perform.

Viewing task statuses
---------------------

You can use the
:meth:`get_status() <fiftyone.utils.cvat.CVATAnnotationResults.print_status>` and
:meth:`print_status() <fiftyone.utils.cvat.CVATAnnotationResults.print_status>`
methods to get information about the current status of the task(s) and job(s)
for that annotation run:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(3)

    view.annotate(
        anno_key,
        label_field="ground_truth",
        segment_size=2,
        task_assignee="user1",
        job_assignees=["user1"],
        job_reviewers=["user2", "user3"],
    )

    results = dataset.load_annotation_results(anno_key)
    results.print_status()

    results.cleanup()
    dataset.delete_annotation_run(anno_key)

.. code-block:: text

    Status for label field 'ground_truth':

        Task 331 (FiftyOne_quickstart_ground_truth):
            Status: annotation
            Assignee: user1
            Last updated: 2021-08-11T15:09:02.680181Z
            URL: http://localhost:8080/tasks/331

            Job 369:
                Status: annotation
                Assignee: user1
                Reviewer: user2

            Job 370:
                Status: annotation
                Assignee: user1
                Reviewer: user3

Using the CVAT API
------------------

You can use the
:meth:`connect_to_api() <fiftyone.utils.cvat.CVATAnnotationResults.connect_to_api>`
to retrive a :class:`CVATAnnotationAPI <fiftyone.utils.cvat.CVATAnnotationAPI>`
instance, which is a wrapper around the
`CVAT REST API <https://openvinotoolkit.github.io/cvat/docs/administration/basics/rest_api_guide/>`_
that provides convenient methods for performing common actions on your CVAT
tasks.

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_api"

    view.annotate(anno_key, label_field="ground_truth")

    results = dataset.load_annotation_results(anno_key)
    api = results.connect_to_api()

    # Launch CVAT in your browser
    api.launch_editor(api.base_url)

    # Get info about all tasks currently on the CVAT server
    response = api.get(api.tasks_url).json()

Deleting tasks
--------------

You can use the
:meth:`delete_task() <fiftyone.utils.cvat.CVATAnnotationAPI.delete_task>`
method to delete specific CVAT tasks associated with an annotation run:

.. code:: python
    :linenos:

    import fiftyone as fo
    import fiftyone.zoo as foz

    dataset = foz.load_zoo_dataset("quickstart")
    view = dataset.take(1)

    anno_key = "cvat_delete_tasks"

    view.annotate(anno_key, label_field="ground_truth")

    results = dataset.load_annotation_results(anno_key)
    api = results.connect_to_api()

    print(results.task_ids)
    # [372]

    api.delete_task(372)
