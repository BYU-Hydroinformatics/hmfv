/*****************************************************************************
 * FILE:    Manage Watersheds JS
 * DATE:    10 March 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var HMFV_MAP = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var attribution,
        projection,
        base_layer,
        first_layer,
        flood_map,
        land_cover,
        flood,
        land,
        layer_obj,
        legend_obj,
        max_depth,
        range_length,
        sources,
        layers,
        view,
        map,
        m_layer_options,
        range_length,
        service_url,
        slider_url,
        sub_folder_str,
        timestep,
        wms_source,
        wms_layer;



    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var find_by,init_vars,init_map,init_legend,init_slider,new_legend_item,indexOf,findByName,raiseLayer,lowerLayer,get_legend_json;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    init_map = function(){
        init_vars();

        projection = ol.proj.get('EPSG:3857');

        attribution = new ol.Attribution({
            html: 'Tiles © <a href="https://services.arcgisonline.com/ArcGIS/' +
            'rest/services/World_Imagery/MapServer">ArcGIS</a>'
        });

        base_layer = new ol.layer.Tile({
            source: new ol.source.XYZ({
                attributions: [attribution],
                url: 'https://server.arcgisonline.com/ArcGIS/rest/services/' + 'World_Imagery/MapServer/tile/{z}/{y}/{x}'
            }),
            name:'BaseLayer'
        });

        sources = [];
        layers = [base_layer];

        first_layer = layer_obj['list'][0];
        jQuery.each(first_layer.metadata,function(key,data){

            wms_source = new ol.source.ImageWMS({
                url:'',
                params:{
                    LAYERS:data.id,
                },
                crossOrigin: 'Anonymous'
            });
            wms_layer = new ol.layer.Image({
                source:wms_source,
                name:data.name
            });
            sources.push(wms_source);
            layers.push(wms_layer);

        });

        sub_folder_str = first_layer.layer.substring(0,first_layer.layer.indexOf('_')+'_'.length);
        slider_url = service_url.replace("rest/","")+sub_folder_str;

        view = new ol.View({
            center: [9111517, 3258918],
            projection: projection,
            zoom: 12,
        });

        map = new ol.Map({
            target: document.getElementById("map"),
            layers: layers,
            view: view,
        });

        map.getView().fit(first_layer.extent,map.getSize());
        map.updateSize();
    };

    init_legend = function(){
        var layr_list;

        layr_list = map.getLayers();
        get_legend_json();

        for(var i= layr_list.getLength();i--;){
            for(var j=legend_obj.layers.length;j--;){
                if(layr_list.item(i).get('name') == legend_obj.layers[j].layerName){
                    new_legend_item(layr_list.item(i),legend_obj.layers[j].legend[0].imageData);
                }
            }
        }

    };




    new_legend_item = function(layer,img){
        var name = layer.get('name');
        var div = "<li data-layerid='" + name + "'>" +
            "<img src='"+"data:image/png;base64,"+img +"'>"+
            "<span> " + name + "</span>" +
            "<i class='glyphicon glyphicon-check lyr'></i> ";
        $('ul.layerstack').prepend(div);
        // $('ul.layerstack li').on('click', function() {
        //            $('ul.layerstack li').removeClass('selected');
        //            $(this).addClass('selected');
        //        });
    };

    get_legend_json = function(){
        $.ajax({
            url: service_url+first_layer.layer+'/MapServer/legend?f=json&callback=',
            type: 'GET',
            async:false,
            dataType: 'json',
            success: function(result){
                legend_obj = result;

            },
            error: function(result){
                console.log(result);
            }
        });

    };


    indexOf = function(layers,layer){
        var length = layers.getLength();
        for (var i = 0; i < length; i++) {
            if (layer === layers.item(i)) {
                return i;
            }
        }
        return -1;
    };

    raiseLayer = function(layer){
        var layers = map.getLayers();
        var index = indexOf(layers, layer);
        if (index < layers.getLength() - 1) {
            var next = layers.item(index + 1);
            layers.setAt(index + 1, layer);
            layers.setAt(index, next);

            // Moves li element up
            var elem = $('ul.layerstack li[data-layerid="' + layer.get('name') + '"]');
            elem.prev().before(elem);
        }

    };

    lowerLayer = function(layer){
        var layers = map.getLayers();
        var index = indexOf(layers, layer);
        if (index > 0) {
            var prev = layers.item(index - 1);
            layers.setAt(index - 1, layer);
            layers.setAt(index, prev);

            // Moves li element down
            var elem = $('ul.layerstack li[data-layerid="' + layer.get('name') + '"]');
            elem.next().after(elem);
        }
    };

    init_vars = function(){
        var $watershed_element = $('#watershed');
        service_url = $watershed_element.attr('data-service-url');
        m_layer_options = $watershed_element.attr('data-layers');
        layer_obj = JSON.parse(m_layer_options);
        timestep = parseFloat($watershed_element.attr('data-timestep'));
        max_depth = parseFloat($watershed_element.attr('data-max-depth'));
        range_length = parseFloat(layer_obj['list'].length);

    };

    init_slider = function(){

        $( "#slider" ).slider({
            value:0,
            min: 0,
            max: max_depth,
            step: timestep,
            animate:"fast",
            slide: function( event, ui ) {

                $( "#amount" ).val( ui.value );
                var decimal_value = ui.value.toString().split(".").join("");

                var url = slider_url+decimal_value+'/MapServer/WmsServer?';

                sources.forEach(function(source){
                    source.setUrl(url);
                });

            }
        });

    };

    findByName = function(name) {
        var layers = map.getLayers();
        var length = layers.getLength();
        for (var i = 0; i < length; i++) {
            if (name === layers.item(i).get('name')) {
                return layers.item(i);
            }
        }
        return null;
    };

    find_by = function(layer, key, value) {

        if (layer.get(key) === value) {
            return layer;
        }

        // Find recursively if it is a group
        if (layer.getLayers) {
            var layers = layer.getLayers().getArray(),
                len = layers.length, result;
            for (var i = 0; i < len; i++) {
                result = find_by(layers[i], key, value);
                if (result) {
                    return result;
                }
            }
        }

        return null;
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
        // Initialize Global Variables
        init_map();
        init_legend();
        init_slider();

        $('.lyr').on('click', function() { var layername = $(this).closest('li').data('layerid');
            var layer = find_by(map.getLayerGroup(), 'name', layername);

            layer.setVisible(!layer.getVisible());

            if (layer.getVisible()) {
                $(this).removeClass('glyphicon-unchecked').addClass('glyphicon-check');
            } else {
                $(this).removeClass('glyphicon-check').addClass('glyphicon-unchecked');
            }
        });

        //Global values.
        var animationDelay = 2000;
        $("#speed").val(animationDelay/1000);
        var sliderInterval = {};

        if($("label[for='amount']").text() == "Flood Depth (meter):"){
            $("#slider").on("slidechange", function(event, ui) {

                var decimal_value = ui.value.toString().split(".").join("");

                var url = slider_url+decimal_value+'/MapServer/WmsServer?';

                sources.forEach(function(source){
                    source.setUrl(url);
                });
                $("#amount").val( ui.value );
            });
            $(".btn-increase").on("click", function() {
                animationDelay = animationDelay + 1000;
                $("#speed").val(animationDelay/1000);
            });
            $(".btn-decrease").on("click", function() {
                animationDelay = animationDelay - 1000;
                $("#speed").val(animationDelay/1000);
            });
            $(".btn-run").on("click", function() {
                //Set the slider value to the current value to start the animation at the correct point.

                var sliderVal = $("#slider").slider("value");
                sliderInterval = setInterval(function() {
                    if($("label[for='amount']").text() == "Flood Depth (meter):"){
                        sliderVal += timestep;
                        $("#slider").slider("value", sliderVal);
                        if (sliderVal===max_depth) sliderVal=0;
                    }else{
                        sliderVal += 1;
                        $("#slider").slider("value", sliderVal);
                        if (sliderVal===range_length) sliderVal=0;
                    }


                }, animationDelay);
            });

            $(".btn-stop").on("click", function() {
                //Call clearInterval to stop the animation.
                clearInterval(sliderInterval);
            });
        }






        $(function () {
            var target, observer, config;
            // select the target node
            target = $('#app-content-wrapper')[0];

            observer = new MutationObserver(function () {
                window.setTimeout(function () {
                    map.updateSize();
                }, 350);
            });

            config = {attributes: true};

            observer.observe(target, config);
        }());

        $('#submit-get-forecast').click(function () {

            var forecast_date = $("#forecast_date_start").val();
            var forecast_stat = $("#forecast_stat_type").val();
            var watershed_id = $("#watershed_info").val();
            var data = new FormData();
            data.append("forecast_date",forecast_date);
            data.append("forecast_stat",forecast_stat);
            data.append("watershed_id",watershed_id);


            var xhr = ajax_update_database_with_file("forecast",data);
            xhr.done(function (result) {
                if('success' in result){
                    $('#container').highcharts({
                        chart: {
                            type:'area',
                            zoomType: 'x'
                        },
                        title: {
                            text: result['title'],
                            style: {
                                fontSize: '11px'
                            }
                        },
                        xAxis: {
                            type: 'datetime',
                            labels: {
                                format: '{value:%d %b %Y}',
                                rotation: 45,
                                align: 'left'
                            },
                            title: {
                                text: 'Date'
                            }
                        },
                        yAxis: {
                            title: {
                                text: result['unit']
                            }

                        },
                        exporting: {
                            enabled: false,
                            width: 5000
                        },
                        series: [{
                            data: result['data'],
                            name: "Streamflow Prediction Tool Forecast"
                        }]

                    });
                    range_length = result['map_forecast'].length;
                    $("label[for='amount']").text("Flood Date");
                    $( "#slider" ).slider({
                        value:1,
                        min: 0,
                        max: result['map_forecast'].length,
                        step: 1,
                        animate:"fast",
                        slide: function( event, ui ) {
                            var range_value = result['map_forecast'][ui.value - 1][1];
                            $( "#amount" ).val(result['map_forecast'][ui.value - 1][0]);
                            var decimal_value = range_value.toString().split(".").join("");

                            var url = slider_url+decimal_value+'/MapServer/WmsServer?';

                            sources.forEach(function(source){
                                source.setUrl(url);
                            });

                        }
                    });
                    $("#amount").val(result['map_forecast'][0][0]);

                    $("#slider").on("slidechange", function(event, ui) {

                        var range_value = result['map_forecast'][ui.value - 1][1];
                        $( "#amount" ).val(result['map_forecast'][ui.value - 1][0]);
                        var decimal_value = range_value.toString().split(".").join("");

                        var url = slider_url+decimal_value+'/MapServer/WmsServer?';

                        sources.forEach(function(source){
                            source.setUrl(url);
                        });
                    });

                    $(".reload").removeClass("hidden");
                    $(".reload").click(function(){
                        location.reload();
                    });



                }
            });


        });

    });



}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
