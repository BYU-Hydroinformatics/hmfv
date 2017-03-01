/*****************************************************************************
 * FILE:    Add Watershed
 * DATE:    2 FEBRUARY 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var HMFV_ADD_WATERSHED = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/




    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var add_watershed,init_jquery,reset_alert,reset_form;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    init_jquery = function(){

    };
    reset_alert = function(){
        $("#message").addClass('hidden');
        $("#message").empty()
            .addClass('hidden')
            .removeClass('alert-success')
            .removeClass('alert-info')
            .removeClass('alert-warning')
            .removeClass('alert-danger');
    };

    reset_form = function(result){
        if("success" in result){
            $("#watershed-name-input").val('');
            $("#service-folder-input").val('');
            $("#spt-watershed-name-input").val('');
            $("#spt-reach-id-input").val('');
            $("#rc-upload-input").val('');
            addSuccessMessage('Watershed Upload Complete!');

        }
    };





    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/



    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        init_jquery();

        add_watershed = function(){

            reset_alert();

            var watershed_name = $("#watershed-name-input").val();
            var service_folder = $("#service-folder-input").val();
            var spt_watershed = $("#spt-watershed-name-input").val();
            var spt_reach = $("#spt-reach-id-input").val();
            var rating_curve_files = $("#rc-upload-input")[0].files;

            if(watershed_name == ""){
                addErrorMessage("Display Name cannot be empty!");
                return false;
            }else{
                reset_alert();
            }
            if(service_folder == ""){
                addErrorMessage("Service Folder cannot be empty!");
                return false;
            }else{
                reset_alert();
            }
            if(spt_watershed == ""){
                addErrorMessage("Streamflow Prediction Tool Watershed cannot be empty!");
                return false;
            }else{
                reset_alert();
            }
            if(spt_reach == ""){
                addErrorMessage("Streamflow Prediction Tool Watershed reachid cannot be empty");
                return false;
            }else{
                reset_alert();
            }
            if($("#rc-upload-input").val() == ""){
                addErrorMessage("Rating Curve File cannot be empty!");
                return false;
            }else{
                reset_alert();
            }

            var data = new FormData();
            data.append("display_name",watershed_name);
            data.append("service_folder",service_folder);
            data.append("spt_watershed",spt_watershed);
            data.append("spt_reach",spt_reach);
            for(var i=0;i < rating_curve_files.length; i++){
                data.append("rating_curve",rating_curve_files[i]);
            }

            var xhr = ajax_update_database_with_file("submit",data);
            xhr.done(function(return_data){
                if("success" in return_data){
                    reset_form(return_data);
                }
            });


        };

        $('#submit-add-watershed').click(add_watershed);

    });



}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.