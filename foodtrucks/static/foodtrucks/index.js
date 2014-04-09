//Holder for current position, default San Francisco
var lat = 37.77493;
var lng = -122.41942;

//Holder for search options 
var radius = 605;         //radius, default to 605m ~= 0.5 mile
var openOnly = false;     //whether display only opening trucks
var foodItems = [];       //food item keywords to match 

//The Map and Markers
var map = null;
var markers = [];

//Holder for truck infos
var truckinfos = [];

//On Load
$(function(){
    /* hide the floating windows other than input bar */
    $("#filter_dialog").hide();
    $("#truck_info").hide();
    $("#truck_list").hide();

    /* set focus on input bar, and add listener to enter key */
    $("#in_address").focus();
    $("#in_address").keypress(function(e){
        code= (e.keyCode ? e.keyCode : e.which);
        // Enter Key Pressed
        if (code == 13) {
            $("#getGeo").trigger("click");
        }
    });

    /* Get user location if allowed */
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(updatePosition);
    }
 
    initializeMap();
    loadTrucks();

    /* Set listener to button click events */
    $("#getGeo").click(function(e) {
        e.preventDefault();
        codeAddress();
    });
    $("#toggleFilter").click(function(e){
        e.preventDefault();
        $("#filter_dialog").slideToggle("fast");
    });
    $("#filter_cancel").click(function(e){
        e.preventDefault();
        $("#filter_dialog").slideUp("fast");
    });
    $("#filter_apply").click(function(e){
        e.preventDefault();
        // update the search options
        var distance = parseFloat($("#distance").val());
        if(!isNaN(distance)) {
            radius = distance * 1609; //miles to meters
        }
        openOnly = $("#checkopenonly").prop("checked");
        foodItems = $("#custom_food").val();
        $("#filter_dialog").slideUp("fast");
        updateMapPosition();
        loadTrucks();
    });
});

/* callback function for html5 navigator */
function updatePosition(position) {
    lat = position.coords.latitude;
    lng = position.coords.longitude;
    updateMapPosition();
}

/* update map according to current center and radius */
function updateMapPosition() {
    var latlng = new google.maps.LatLng(lat,lng);
    map.setCenter(latlng);
    // build a circle and fit the map to circle bounds
    var circleOptions = {
        center: latlng,
        fillOpacity: 0,
        strokeOpacity:0,
        map: map,
        radius: radius
    }
    var radiusCircle = new google.maps.Circle(circleOptions);
    map.fitBounds(radiusCircle.getBounds());
}

/* initialize the map object and map control positions */
function initializeMap() {
    var mapOptions = {
        center: new google.maps.LatLng(lat,lng),
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.BOTTOM_CENTER
        },
        panControl: true,
        panControlOptions: {
            position: google.maps.ControlPosition.TOP_RIGHT
        },
        zoomControl: true,
        zoomControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM
        },
        streetViewControl: true,
        streetViewControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM
        },
        zoom: 10
    };
    map = new google.maps.Map(document.getElementById("map_view"), mapOptions);
    updateMapPosition();
}

/* use google geocoder to code address to latlng coords */
function codeAddress() {
    var address = $("#in_address").val();
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode( { 'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            lat = results[0].geometry.location.lat();
            lng = results[0].geometry.location.lng();
            updateMapPosition();
        } else {
            alert("Geocode was not successful for the following reason: " + status);
        }
    });
}
/* call the backend to load the trucks according to filter options */
function loadTrucks() {
    removeMarkers();
    //get the filter vars and pass to ajax call.
    var data = {
        openOnly:openOnly,
        foodItems:foodItems
    };
    //for each result got from ajax call, create a marker and store the data obj for info display
    $.get('get_trucks/',data,function(data){
        $.each(data, function(i, pos){
            var marker = new google.maps.Marker({
                map: map,
                position: new google.maps.LatLng(pos.lat,pos.lng),
                icon: "/static/foodtrucks/images/foodtruckicon.png",
                title: pos.name
            });
            markers.push(marker);
            var truckinfo = pos;
            truckinfos.push(truckinfo); 
            google.maps.event.addListener(marker, "click", function(){
                var elem = $("#truck_info");
                elem.hide();
                elem.html(getTruckInfoHtml(truckinfo));
                elem.slideDown("fast");
            });                   
        });
    });
}

/* remove all the markers from map and release the refs */
function removeMarkers() {
    for(var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    markers = [];
    truckinfos = [];
}

/* transform the truck_info data object to html */
function getTruckInfoHtml(truck_info) {
    //name
    var in_html = "<p><strong>"+truck_info.name+"</strong></p>";
    //address
    in_html += "<p>"+truck_info.address+"</p>";
    //info url (google search)
    var search_uri = encodeURI('http://www.google.com/#q=' + truck_info.name + " San Francisco");
    in_html += "<p><a href='" + search_uri +"' target='_blank'>more info...</a></p>";
    //opening info
    if(truck_info.opennow) {
        in_html += "<p style='color:#080'><strong>Open</strong></p>";
    } else {
        in_html += "<p style='color:#800'><strong>Closed</strong></p>";
    }
    //schedule info
    in_html += "<p><strong>Schedule Today:</strong></p>";
    for(var i = 0; i < truck_info.schedule.length; i++) {
        in_html += "<p style='margin-left:20px'>" + truck_info.schedule[i][0] +" - " + truck_info.schedule[i][1]+"</p>";
    }
    if(truck_info.schedule.length == 0) in_html += "<p style='margin-left:20px'>Closed</p>";
    return in_html;
}
