(function($) {
    console.log( 'server loaded' );

    d3.csv('https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv', function(err, rows){
function unpack(rows, key) {
  return rows.map(function(row) { return row[key]; });
}
var z_data=[ ]
for(i=0;i<24;i++)
{
  z_data.push(unpack(rows,i));
}

var data = [{
  z: z_data,
  type: 'surface',
  contours: {
    z: {
      show:true,
      usecolormap: false,
      highlightcolor:"#42f462",
      project:{z: true}
    }
  }
}];

var layout = {
  scene: {camera: {eye: {x: 1.87, y: 0.88, z: -0.64}}},
  autosize: true,
  width: '100%',
  height: 500,
  margin: {
    l: 65,
    r: 50,
    b: 65,
    t: 90,
  }
};

Plotly.newPlot('tester', data, layout);
});


})(jQuery);