//////////////////////////////////////////////////////////////
//////////////////////// Radar chart Set-Up //////////////////
//////////////////////////////////////////////////////////////

//var color = d3.scale.ordinal().range(["#EDC951","#CC333F","#00A0B0"]); to pick specific colors

var margin = {top: 100, right: 100, bottom: 100, left: 100},
    legendPosition = {x: 50, y: 100},
    width = Math.min(500, window.innerWidth - 10) - margin.left - margin.right,
    height = Math.min(width, window.innerHeight - margin.top - margin.bottom - 20);

//////////////////////////////////////////////////////////////
//////////////////// Draw the Chart //////////////////////////
//////////////////////////////////////////////////////////////
var radarChartOptions = {
  w: width,
  h: height,
  margin: margin,
  legendPosition: legendPosition,
  maxValue: 1,
  wrapWidth: 60,
  levels: 5,
  roundStrokes: true,
  color: d3.scale.category20(),
  axisName: "measure",
  areaName: "track",
  value: "value",
  uri: "uri"
};

function RefreshData(artist_uris){
    //Get data from Spotify, Update player with 1st result, Load the data and Call function to draw the Radar chart
    var players = $();
    var urisSTR = artist_uris.join()
    d3.json('/_audio_features_datacall_multi?artists_uris=' + urisSTR, function(error, data){
        data.features.forEach(function(item){
            var uri_ID = item['values'][0]['uri'].split(':')[2]
            var player = '<iframe class="spotify-player" id=' + uri_ID +
                ' src=https://open.spotify.com/embed?uri=' + item['values'][0]['uri'] +
                ' width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
            players = players.add(player);
        });
        $('.spotify-player').remove();
        $('#player-div').append(players);
        $(players[0]).show();
        RadarChart(".radarChart", data.features, radarChartOptions);
    });
}

//Load the data and Call function to draw the Radar chart
//d3.json('/_audio_features_datacall', function(error, data){
//    RadarChart(".radarChart", data.features, radarChartOptions);
//});
//TODO: load in artist list objects, currently hardcoded on first load. Change so can inistiate with list of URIs and populate everything
RefreshData(['spotify:artist:5cMgGlA1xGyeAB2ctYlRdZ', 'spotify:artist:7bcbShaqKdcyjnmv4Ix8j6', 'spotify:artist:0asVlqTLu3TimnYVyY5Jxi'])

$(function() {
    $("#artist_input").autocomplete({
          source: function(request, response){
            $.ajax({
              url: "/_artist_search",
              dataType: "json",
              data: {
                q: request.term
              },
              success: function(data){
                response(data.matching_results);
              }
            });
          },
          minLength: 2,
          focus: function (event, ui) {
            //handled in css
           },
          select: function(event, ui){
            var uris = [];
            var uri = ui.item.uri.split(':')[2] //get just ID (should refactor to use just that)
            $('#artist-list').prepend($('#' + uri))
            $('#artist-list li:gt(2)').remove(); //max 3 artists to compare
            //get comma sepearated list of artist uris (stripped IDs) from all current list items
            $('#artist-list').find('li').each(function(){uris.push('spotify:artist:' + this.id);});
            RefreshData(uris)
          }
    })
    .autocomplete("instance")._renderItem = function(ul, item){
      //set li id as item uri, split to get last part (ex. spotify:artist:7BMccF0hQFBpP6417k1OtQ)
      return $("<li id=" + item.uri.split(':')[2] + ">")
        .append("<div class='ui-menu-item-wrapper'><img src=" + item.icon_img + " class='circular artist-icon'>" + item.name + "</div>")
        .appendTo(ul);
    };
});

//TODO: get this working, on click of artist item, update player -- on click isn't even triggered so far
$('.artist-item').click(function(e){
    console.log('ui menu item click!!!!!!!!')
   //$('#player').attr('src', 'https://open.spotify.com/embed?uri=spotify:artist:' + $(e.target).attr('id'))
});

$('#test').click(function(){
    console.log('test clicked')
})

$('.ui-menu-item').click(function(e){
    console.log('ui menu item clicked!!!!!!!!!')
   //$('#player').attr('src', 'https://open.spotify.com/embed?uri=spotify:artist:' + $(e.target).attr('id'))
});