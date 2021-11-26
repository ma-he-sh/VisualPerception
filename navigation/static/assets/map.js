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

function postReq( url, data, callback ) {
	$.post( url, data, callback );
}

function getReq( url, data, callback ) {
	$.get( url, data, callback );
}

(function($) {
    console.log( 'server loaded' );

	var goals = {
		'x': [],
		'y': [],
		'z': [],
	}
	var solution = {
		'x': [],
		'y': [],
		'z': []
	}
	var mapHandler = new MapHandler( grid_pos, obstacle_pos )
	grid_rows = mapHandler.get_grid_map();
	obstacle_rows = mapHandler.get_obstacle_map();

	var grid_map = {
		x:grid_rows['x'], y: grid_rows['y'], z: grid_rows['z'],
		mode: 'markers',
		marker: {
			size: 1,
			line: {
				color: 'rgba(255, 255, 255, 1)',
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

	var solution_3d = {
		x: solution['x'], y: solution['y'], z: solution['z'],
		mode: 'line+markers',
		marker: {
			size: 4,
			line: {
				color: 'rgba(255, 217, 217, 0.14)',
				width: 1,
			},
			opacity: 1,
		},
		type: 'scatter3d'
	}

	var data = [grid_map, obstacles, solution_3d];
	var layout = {
		margin: {
			l: 0,
			r: 0,
			b: 0,
			t: 0,
			pad: 100
		},
		yaxis: {
			dticks: 10,
		},
		xaxis: {
			dticks: 10,
		},
		paper_bgcolor: 'rgb(0, 0, 0)',
		plot_bgcolor: 'rgb(0, 0, 0)',
		autosize: true,
		height: 1080,
		showlegend: false,
	};
	Plotly.newPlot('grid_map', data, layout);
	
	// 2d graph of the motion planning
	var path_points = {
		x: grid_rows['x'], y: grid_rows['y'],
		mode: 'markers',
		marker: {
			size: 4,
			color: 'rgb(255, 255, 255)',
			line: {
				color: 'rgba(255, 0, 0, 0)',
				width: 1,
			},
			opacity: 0.25
		},
		type: 'scatter'
	};
	var goal_points = {
		x: goals['x'], y: goals['y'],
		mode: 'markers',
		marker: {
			size: 20,
			line: {
				color: 'rgba(255, 255, 0, 0)',
				width: 1,
			},
			opacity: 1
		},
		type: 'scatter'
	};
	var obstacles2 = {
		x:obstacle_rows['x'], y: obstacle_rows['y'],
		mode: 'markers',
		marker: {
			size: 4,
			line: {
				color: 'rgba(255, 217, 217, 0.14)',
				width: 1,
			},
			opacity: 1
		},
		type: 'scatter'
	};
	var solution_path = {
		x: solution['x'], y: solution['y'],
		mode: 'marker',
		marker: {
			size: 2,
			line: {
				color: 'rgba(255, 217, 217, 0.14)',
				width: 1,
			},
			opacity: 1,
		},
		type: 'line'
	}
	var layout2 = {
		margin: {
			l: 0,
			r: 0,
			b: 0,
			t: 0,
			pad: 100
		},
		yaxis: {
			dticks: 10,
		},
		xaxis: {
			dticks: 10,
		},
		paper_bgcolor: 'rgb(0, 0, 0)',
		plot_bgcolor: 'rgb(0, 0, 0)',
		autosize: true,
		height: 600,
		showlegend: false,
	};
	var data2 = [path_points, obstacles2, goal_points, solution_path ];
	Plotly.newPlot('path_map', data2, layout2);

	// click handler
	var plot = document.getElementById('path_map');
	plot.on('plotly_click', on_node_click);

	function on_node_click(data) {
		var point = data.points[0];
		goals['x'].push(point.x);
		goals['y'].push(point.y);

		Plotly.newPlot("path_map", data2, layout2); 
		plot.removeEventListener('plotly_click', on_node_click);
		plot.on('plotly_click', on_node_click);
	}

	// submit start and goal point
	$(document).on('click', '[data-action]', function() {
		if (goals == undefined) {
			return;
		}

		var map_id = $(this).data('map-id');

		var data = {
			'startx': goals['x'][0],
			'starty': goals['y'][0],
			'endx'  : goals['x'][1],
			'endy'  : goals['y'][1],
			'map_id': map_id,
		}

		postReq("/set_robot_goals", data, function(resp) {
			if( resp.success ) {
				var path = resp.path;
				console.log( path );
				if( path.length > 0 ) {
					path.forEach( function( point, index ) {
						solution['x'].push( point[0] );
						solution['y'].push( point[1] );
						solution['z'].push( 1 );
					});
					// clear goals 
					goals['x'] = []
					goals['y'] = []
					goals['z'] = []
					Plotly.newPlot( "path_map", data2, layout2 );
					plot.removeEventListener('plotly_click', on_node_click );
					plot.on('plotly_click', on_node_click );
				}
			} else {
				console.error( resp );
			}
		});
	});
})(jQuery);
