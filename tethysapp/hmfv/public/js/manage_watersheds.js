/*****************************************************************************
 * FILE:    Manage Watersheds JS
 * DATE:    3 March 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var HMFV_MANAGE_WATERSHEDS = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var public_interface;				// Object returned by the module
    var m_uploading_data, m_results_per_page;



    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var initializeTableFunctions, initializeModal, getTablePage, displayResultsText,
        getModalHTML;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //Show a modal when the user clicks Edit.
    getModalHTML = function(watershed_id, reload) {
        reload = typeof reload !== 'undefined' ? reload : false;
        $.ajax({
            url: 'edit',
            method: 'GET',
            data: {
                'watershed_id': watershed_id
            },
            success: function(data) {
                $("#edit_watershed_modal").find('.modal-body').html(data);
                initializeModal(); //Get the relevant metadata for the selected watershed.
                if (reload) {
                    addSuccessMessage("Watershed Update Complete!");
                }
            }
        });
    };

    initializeModal = function() {

        $('.bootstrap-switch').each(function () {
            $(this).bootstrapSwitch();
        }); //Enable bootstrap switch

        $('.rc_upload').addClass('hidden');

        //show hide elements based on shape upload toggle selection
        $('#rc-upload-toggle').on('switchChange.bootstrapSwitch', function(event, state) {

            var state=$(this).bootstrapSwitch('state');//returns true or false
            if(state) {
                //show file upload
                $('.rc_upload').removeClass('hidden');
            } else {
                $('.rc_upload').addClass('hidden');
            }
        }); //Show the option to upload rating curve based on the switch

        $('#edit_modal_submit').off().click(function () {
            window.scrollTo(0,0);
            $('#message').addClass('hidden');
            //clear message div
            $('#message').empty()
                .addClass('hidden')
                .removeClass('alert-success')
                .removeClass('alert-info')
                .removeClass('alert-warning')
                .removeClass('alert-danger');

            var submit_button = $(this);

            //Getting the values of the newly edited watershed form
            var watershed_id = $("#watershed_id").val();
            var watershed_name = $("#watershed-name-input").val();
            var service_folder = $("#service-folder-input").val();
            if (service_folder.substr(-1) !== "/") {
                service_folder = service_folder.concat("/");
            }
            var spt_watershed = $("#spt-watershed-name-input").val();
            var spt_basin = $("#spt-basin-name-input").val();
            var spt_reach = $("#spt-reach-id-input").val();
            submit_button.text('Submitting ...');

            //If the user wants to re-upload the shapefile follow the following workflow
            if ($('#shp-upload-toggle').bootstrapSwitch('state')) {
                //Following the same workflow as adding a watershed
                var rating_curve_files = $("#rc-upload-input")[0].files;
                var data = new FormData(); //Preparing the data to be uploaded by the edit watershed modal
                data.append("watershed_id",watershed_id);
                data.append("display_name",watershed_name);
                data.append("service_folder",service_folder);
                data.append("spt_watershed",spt_watershed);
                data.append("spt_basin",spt_basin);
                data.append("spt_reach",spt_reach);
                for(var i=0;i < rating_curve_files.length; i++){
                    data.append("rating_curve",rating_curve_files[i]);
                }
                var xhr = ajax_update_database_with_file("submit",data);
                xhr.done(function(return_data){
                    if("success" in return_data){
                        getModalHTML(watershed_id, true);
                        submit_button.text('Save Changes');
                    }
                });

            }else{
                var data = new FormData(); //If there is no new rating curve, simply update the database without the file
                data.append("watershed_id",watershed_id);
                data.append("display_name",watershed_name);
                data.append("service_folder",service_folder);
                data.append("spt_watershed",spt_watershed);
                data.append("spt_basin",spt_basin);
                data.append("spt_reach",spt_reach);
                var xhr = ajax_update_database("submit",data);
                xhr.done(function(return_data){
                    if("success" in return_data){
                        getModalHTML(watershed_id, true);
                        submit_button.text('Save Changes');
                    }
                });
            }

        });

    };

    //Initialize the table showing each watershed from the local database
    initializeTableFunctions = function() {
        m_results_per_page = 5;
        //handle the submit edit event
        $('.submit-edit-watershed').off().click(function () {
            //Get the form to edit the watershed
            getModalHTML($(this).parent().parent().parent().find('.watershed-name').data('watershed_id'));
        });


        //handle the submit update event
        $('.submit-delete-watershed').off().click(function () {
            var data = {
                watershed_id: $(this).parent().parent().parent().find('.watershed-name').data('watershed_id')
            };
            //update database
            var xhr = deleteRowData($(this), data, "main_message");
            if (xhr != null) {
                xhr.done(function (data) {
                    if('success' in data) {
                        var num_watersheds_data = $('#manage_watershed_table').data('num_watersheds');
                        var page = parseInt($('#manage_watershed_table').data('page'));
                        $('#manage_watershed_table').data('num_watersheds', Math.max(0, parseInt(num_watersheds_data) - 1));
                        if (parseInt($('#manage_watershed_table').data('num_watersheds')) <= m_results_per_page * page) {
                            $('#manage_watershed_table').data('page', Math.max(0, page - 1));
                        }
                        getTablePage();
                    }
                });
            }
        });

        displayResultsText();

        if (m_results_per_page >= $('#manage_watershed_table').data('num_watersheds')) {
            $('[name="prev_button"]').addClass('hidden');
            $('[name="next_button"]').addClass('hidden');
        }

        //pageination next and previous button update
        $('[name="prev_button"]').click(function(){
            var page = parseInt($('#manage_watershed_table').data('page'));
            $('#manage_watershed_table').data('page', Math.max(0, page-1));
            getTablePage();
        });
        $('[name="next_button"]').click(function(){
            var page = parseInt($('#manage_watershed_table').data('page'));
            $('#manage_watershed_table').data('page', Math.min(page+1,
                Math.floor(parseInt($('#manage_watershed_table').data('num_watersheds')) / m_results_per_page - 0.1)));
            getTablePage();
        });
    };

    displayResultsText = function() {
        //dynamically show table results display info text on page
        var page = parseInt($('#manage_watershed_table').data('page'));
        var num_watersheds_data = $('#manage_watershed_table').data('num_watersheds');
        var display_min;
        if (num_watersheds_data == 0){
            display_min = 0
        }
        else{
            display_min = ((page + 1) * m_results_per_page) - (m_results_per_page - 1);
        }
        var display_max = Math.min(num_watersheds_data, ((page + 1) * m_results_per_page));
        $('[name="prev_button"]').removeClass('hidden');
        $('[name="next_button"]').removeClass('hidden');
        if (page == 0){
            $('[name="prev_button"]').addClass('hidden');
        } else if (page == Math.floor(num_watersheds_data / m_results_per_page - 0.1)) {
            $('[name="next_button"]').addClass('hidden');
        }
        if (num_watersheds_data != 0) {
            $('#display-info').append('Displaying watersheds ' + display_min + ' - '
                + display_max + ' of ' + num_watersheds_data);
        }else {
            $('#display-info').append('No watersheds to display' + '<br>To add one, ' +
                'click <a href="../add-watershed">here</a>.');
        }
    };

    //Get the page number
    getTablePage = function() {
        $.ajax({
            url: 'table',
            method: 'GET',
            data: {'page': $('#manage_watershed_table').data('page')},
            success: function(data) {
                $("#manage_watershed_table").html(data);
                initializeTableFunctions();
            }
        });
    };

    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/

    public_interface = {

    };

    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        // Initialize Global Variables
        m_uploading_data = false;
        getTablePage();
        $('#edit_modal_submit').removeAttr('data-dismiss');
        $('#edit_watershed_modal').on('hidden.bs.modal', function () {
            $("#edit_watershed_modal").find('.modal-body').html('<p class="lead">Loading ...</p>');
            getTablePage();
        });
    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.