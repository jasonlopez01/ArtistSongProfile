//////////////////////////////////////////////////////////////
//////////////////////// Radar chart Set-Up //////////////////
//////////////////////////////////////////////////////////////

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
  color: d3.scale.category20(), //color,
  axisName: "measure",
  areaName: "track",
  value: "value",
  uri: "uri"
};

function RefreshData(artist_uri){
    //Get data from Spotify, Update player with 1st result, Load the data and Call function to draw the Radar chart
    var players = $();
    d3.json('/_audio_features_datacall/' + artist_uri, function(error, data){
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
    //RadarChart(".radarChart", data.features, radarChartOptions);
//});
RefreshData('spotify:artist:0asVlqTLu3TimnYVyY5Jxi')

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
            $('#artist_label').html(ui.item.name);
            $('.artist-img').attr('src', ui.item.artist_img)
            RefreshData(ui.item.uri)
          }
    })
    .autocomplete("instance")._renderItem = function(ul, item){
      var uri_ID = item.uri.split(':')[2]
      return $("<li id=" + uri_ID + ">")
        .append("<div class='ui-menu-item-wrapper'><img src=" + item.icon_img + " class='circular artist-icon'>" + item.name + "</div>")
        .appendTo(ul);
    };
});