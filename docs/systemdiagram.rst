Diagram of system components
============================

.. graphviz::

    digraph {

      // Define global style settings
      graph [pad="0.25", ranksep="0.5", nodesep="0.75" colorscheme=rdylbu10];
      node [fixedsize=true width=2.5 height=1.0 fontsize=10 margin="0.0,0.0" shape="rectangle" style="filled, rounded, bold" fillcolor="#ffffff" fontname="Helvetica" colorscheme=rdylbu10];

      // Reset the ranking
      newrank=true;

      // Force lines between boxes to be orthogonal
      splines=ortho;

      // Define the things on the server
      subgraph cluster_server {

         label="OpenREM server";
         tooltip="OpenREM server";
         fontname="Helvetica";
         fontsize=14;
         style=filled;
         color=5;
         //node [style=filled color=white];

         // Define the nodes for the data storage, display and retrieval
         webserver [fontsize="8" label=<
         <FONT POINT-SIZE="10"><B>Webserver</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />See note 1 below
         >];

         python_django [fontsize="8" label=<
         <FONT POINT-SIZE="10"><B>OpenREM</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />Python Django app
         >];

         database [fontsize="8" shape="cylinder" fillcolor=8 label=<
         <FONT POINT-SIZE="10"><B>Database</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />See note 3 below
         >];

         python_task_queue [fontsize="8" label=<
         <FONT POINT-SIZE="10"><B>Python task queue</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />Manages internal processes such
         <BR ALIGN="CENTER" />as queries, imports, exports, and
         <BR ALIGN="CENTER" />skin dose map calculation
         >];

         skin_dose_map_data [fontsize="8" shape="box" label=<
         <FONT POINT-SIZE="10"><B>Skin dose mapping</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />Data calculation, storage
         <BR ALIGN="CENTER" />and retrieval
         >];

         server_media_folder [fontsize="8" shape="folder" fillcolor=8 label=<
         <FONT POINT-SIZE="10"><B>Server file storage</B></FONT>
         >];

         data_export [fontsize="8" shape="box" label=<
         <FONT POINT-SIZE="10"><B>Data export</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />To server file system
         <BR ALIGN="CENTER" />for user download
         >];

         // Define the links between the data storage, display and retrieval
         webserver -> python_django [dir=both];
         python_django -> database [dir=both];
         python_django -> python_task_queue [dir=both];
         python_task_queue -> skin_dose_map_data;
         python_task_queue -> data_export;
         skin_dose_map_data -> server_media_folder [dir=both];
         //skin_dose_map_data -> python_django [style=dotted dir=both];
         data_export -> server_media_folder [dir=both];
         //data_export -> python_django [style=dotted dir=both];

         // Define the nodes for the DICOM store, database population and skin dose map calculation
         orthanc [fontsize="8" shape="box" label=<
         <FONT POINT-SIZE="10"><B>DICOM storage</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />See note 2 below
         >];

         orthanc_script [fontsize="8" shape="diamond" fillcolor=4 label=<
         <FONT POINT-SIZE="10">Does the object</FONT>
         <BR ALIGN="CENTER" /><FONT POINT-SIZE="10">contain useful data?</FONT>
         >];

         populate_database [fontsize="8" shape="box" label=<
         <FONT POINT-SIZE="10"><B>Extract information</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />from the DICOM object
         <BR ALIGN="CENTER" />to the OpenREM database
         >];

         delete_object [fontsize="8" shape="box" label=<
         <FONT POINT-SIZE="10"><B>Delete the DICOM object</B></FONT>
         <BR ALIGN="CENTER" />
         <BR ALIGN="CENTER" />from the Orthanc DICOM store
         >];

         calc_skin_dose_map [fontsize="8" shape="diamond" fillcolor=4 label=<
         <FONT POINT-SIZE="10">Calculate</FONT>
         <BR ALIGN="CENTER" /><FONT POINT-SIZE="10">skin dose map?</FONT>
         >];

         // Define the links between the DICOM store, database population and skin dose map calculation
         orthanc_script -> populate_database [fontsize="10" fontcolor="darkgreen" label=<<FONT FACE="Helvetica"><B>Yes</B></FONT>>];
         populate_database -> delete_object;
         orthanc_script -> delete_object [fontsize="10" fontcolor="red" label=<<FONT FACE="Helvetica"><B>No</B></FONT>>];
         orthanc -> orthanc_script;
         populate_database -> calc_skin_dose_map;

         // Define the links between the two groups
         python_django -> populate_database [dir=back];
         //calc_skin_dose_map -> python_task_queue [style=dotted label="Yes" fontcolor=darkgreen fontsize=8]
         calc_skin_dose_map -> python_task_queue [fontsize="10" fontcolor="darkgreen" label=<<FONT FACE="Helvetica"><B>Yes</B></FONT>>];

         // Force certain nodes to be on the same level so that the diagram looks good
         //{rank=same; webserver orthanc};
         //{rank=same; python_task_queue calc_skin_dose_map };
         //{rank=same; python_task_queue skin_dose_map_data };
         //{rank=same; data_export server_media_folder };
         //{rank=same; python_django->blank_node_1->delete_object->populate_database [style=invis]; rankdir=LR;}
         //{rank=same; database->populate_databse->delete_object [style=invis]; rankdir=LR;}
         //{rank=same; python_django populate_database orthanc_script; rankdir=LR;}
         //{rank=same; database populate_database delete_object; rankdir=LR;}
         //{rank=same; database python_django populate_database; rankdir=LR;}
         //{rank=same; python_task_queue calc_skin_dose_map; rankdir=LR;}
         {rank=same; database populate_database delete_object; rankdir=LR;}
         {rank=same; skin_dose_map_data -> server_media_folder -> data_export[style="invis"]; rankdir=LR;}
      }

      // Define the web browser, modality and pacs nodes
      web_browser [fontsize="8" fillcolor=3 label=<
      <FONT POINT-SIZE="10"><B>Client web browser</B></FONT>
      <BR ALIGN="CENTER" />
      <BR ALIGN="CENTER" />Access to tabulated data, filters,
      <BR ALIGN="CENTER" />charts, exports, skin dose maps
      >];

      modality [fontsize="8" fillcolor=6 shape="parallelogram" label=<
      <FONT POINT-SIZE="10"><B>X-ray imaging modalities</B></FONT>
      <BR ALIGN="CENTER" />
      <BR ALIGN="CENTER" />e.g. X-ray CT scanners,
      <BR ALIGN="CENTER" />fluoroscopy systems,
      <BR ALIGN="CENTER" />x-ray rooms
      >];

      pacs [fontsize="8" fillcolor=6 shape="parallelogram" label=<
      <FONT POINT-SIZE="10"><B>PACS</B></FONT>
      >];

      //blank_node_2 [label="" shape=none];

      // Define the links that the browser, modality and pacs have
      web_browser -> webserver [dir=both];
      modality -> orthanc;
      pacs -> orthanc;

      // Force the web browser, blank node, modality and pacs to be on the same level in a specific order
      //{rank=same; web_browser modality pacs; rankdir=LR;};
    }


Alternatives
------------

1: Web servers
^^^^^^^^^^^^^^
The recommended web server for Windows is Microsoft IIS - see *to be written* docs for details. This
has replaced the recommendation to use Apache due to difficulties in obtaining the
required binary files, as described in the :ref:`webservers` section of the installation document.

The recommended web server for Linux is Gunicorn with NGINX - see :ref:`Install Linux webserver` for details.

Alternatively, a built-in web server is included that will suffice for testing purposes and getting started.

2: DICOM Store node
^^^^^^^^^^^^^^^^^^^
Any DICOM Store can be used, as long as it can be used to call the OpenREM import script. See :doc:`netdicom-nodes` for
more details. Orthanc is the recommended DICOM Store services to use; it is installed by default in Docker, see
:ref:`dicom_store_scp_linux` for Linux installation, *to be written* for Windows installation, and the
:ref:`configure_third_party_DICOM` section for configuration help.

3: Database
^^^^^^^^^^^
PostgreSQL is the recommended database to use with OpenREM. It is the only database that OpenREM will calculate
median values for charts with. Other databases can be used with varying capabilities; see the `Django documentation
<https://docs.djangoproject.com/en/1.8/ref/databases/>`_ for more details. For testing only, the built-in SQLite3
database can be used, but this is not suitable for later migration to a production database.
