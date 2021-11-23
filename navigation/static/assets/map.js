class MapHandler {
	constructor( grid_map, obstacles ) {
		this.grid_map = grid_map;
		this.obstacles= obstacles;
	}

	get_grid_map() {
		var map = {
			'x' : [],
			'y' : [],
			'z' : [],
		}

		var x = [];
		var y = [];
		var z = [];	

		var row_index = 0;
		this.grid_map.forEach(function(row, i) {
			row.forEach(function(obj, j) {
				x.push( obj[0] );
				y.push( obj[1] );
				z.push( 1 );
			});
			row_index += 1;
		});

		var map = {
			'x' : x,
			'y' : y,
			'z' : z,
		}

		// console.log( map['x'].length, map['y'].length, this.grid_map )

		return map;
	}

	get_obstacle_map() {
		var map = {
			'x' : [],
			'y' : [],
			'z' : [],
		}

		var x = [];
		var y = [];
		var z = [];	

		var row_index = 0;
		this.obstacles.forEach(function(row, i) {
			row.forEach(function(obj, j) {
				x.push( obj[0] );
				y.push( obj[1] );
				z.push( 1 );
			});
			row_index += 1;
		});

		var map = {
			'x' : x,
			'y' : y,
			'z' : z,
		}

		// console.log( map['x'].length, map['y'].length, this.grid_map )

		return map;
	}
}

(function($) {
    console.log( 'server loaded' );

	var mapHandler = new MapHandler( grid_pos, obstacle_pos )
	grid_rows = mapHandler.get_grid_map();
	obstacle_rows = mapHandler.get_obstacle_map();

	var grid_map = {
		x:grid_rows['x'], y: grid_rows['y'], z: grid_rows['z'],
		mode: 'markers',
		marker: {
			size: 1,
			line: {
				color: 'rgba(255, 217, 217, 0.14)',
				width: 1,
			},
			opacity: 0.2
		},
		type: 'scatter3d'
	};

	var obstacles = {
		x:obstacle_rows['x'], y: obstacle_rows['y'], z: obstacle_rows['z'],
		mode: 'markers',
		marker: {
			size: 4,
			line: {
				color: 'rgba(255, 217, 217, 0.14)',
				width: 1,
			},
			opacity: 1
		},
		type: 'scatter3d'
	};

	var data = [grid_map, obstacles];
	var layout = {
		margin: {
			l: 0,
			r: 0,
			b: 0,
			t: 0,
			pad: 100
		},
		paper_bgcolor: 'rgb(0, 0, 0)',
		autosize: true,
		height: 800
	};
	Plotly.newPlot('grid_map', data, layout);

})(jQuery);