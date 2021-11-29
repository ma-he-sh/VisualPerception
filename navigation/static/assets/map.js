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
	var map_timer;
	var global_map_id;
	var global_end_goal;

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

	var robot_pos = {
		'x': [],
		'y': [],
		'z': [],
	}

	var new_obstacles = {
		'x': [],
		'y': [],
		'z': [],
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
			size: 10,
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
				width: 10,
			},
			opacity: 1,
		},
		type: 'line'
	}
	//======================
	// robot position handle
	var curr_robot_pos = {
		x:robot_pos['x'], y: robot_pos['y'],
		mode: 'markers',
		marker: {
			size: 20,
			line: {
				color: 'rgba(255, 0, 0, 0.14)',
				width: 1,
			},
			opacity: 1
		},
		type: 'scatter'
	}
	var new_obstacles_pos = {
		x:new_obstacles['x'], y: new_obstacles['y'],
		mode: 'markers',
		marker: {
			size: 20,
			line: {
				color: 'rgba(0, 217, 217, 0.14)',
				width: 1,
			},
			opacity: 1
		},
		type: 'scatter'
	}
	// =====================
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
	var data2 = [path_points, obstacles2, goal_points, solution_path, curr_robot_pos, new_obstacles_pos ];
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

	// obstacle validate already synced
	function new_obstacle_synced( obstacle_pos ) {
		console.log('sync check');
		var obs_len =  new_obstacles['x'].length;
		var new_obs_len = obstacle_pos.length;

		var data_synced = (obs_len == new_obs_len);
		console.log('data synced=', data_synced, ' obs_len=', obs_len, ' new_obs_len=', new_obs_len );
		return data_synced;
	}

	var rest_requesting = false;
	// start pinging for status
	function get_latest_status() {
		if( rest_requesting ) return;

		console.log('start ping', global_map_id );
		var data = {
			map_id: global_map_id,
		}
		rest_requesting = true;
		getReq("/robot_status", data, function(resp){
			rest_requesting = false;
			if( resp.success ) {
				var obstacle_pos = resp.obstacle_pos;
				var curr_robot_pos    = resp.robot_pos;

				var update_map = false;
				if ( robot_pos['x'][0] != curr_robot_pos[0] && robot_pos['y'][0] != curr_robot_pos[1] ) {
					// console.log('updated here1')
					robot_pos['x'][0] = curr_robot_pos[0];
					robot_pos['y'][0] = curr_robot_pos[1];
					robot_pos['z'][0] = 1;

					update_map = true;
				}

				if ( obstacle_pos.length > 0 ) {
					var obstacles_synced = new_obstacle_synced( obstacle_pos );
					if( !obstacles_synced ) {
						console.log('updated here2');

						var last_index = obstacle_pos[ obstacle_pos.length - 1 ];
						if( last_index ) {
							new_obstacles['x'].push( last_index[0] );
							new_obstacles['y'].push( last_index[1] );
							new_obstacles['z'].push( 1 );

							update_map = true;
						}
					}
				}

				//console.log( 'update_map', update_map );

				// update map
				if ( update_map ) {
					Plotly.newPlot( "path_map", data2, layout2 );
					plot.removeEventListener('plotly_click', on_node_click );
					plot.on('plotly_click', on_node_click );

					// stop the timer
					clearInterval( map_timer );

					// set new start position and create new path
					// clear current motion plan
					$('.motion_plan_wrapper').html('');
					// clear current data
					Plotly.deleteTraces("path_map", 3); // 3rd index is the solution path
					// end

					// clean solutions
					solution = {'x':[],'y':[],'z':[]}

					// set new start goal
					goals['x'][0] = curr_robot_pos[0];
					goals['y'][0] = curr_robot_pos[1];
					goals['x'][1] = global_end_goal[0];
					goals['y'][1] = global_end_goal[1];

					// set new robot position
					var data = {
						'startx': curr_robot_pos[0],
						'starty': curr_robot_pos[1],
						'endx'  : global_end_goal[0],
						'endy'  : global_end_goal[1],
						'map_id': global_map_id,
						'reset_obstacles': 0,
					}

					// set robot goals and plan the new motion
					set_robot_goals( global_map_id, data );
				}
			} 
		});
	}

	// render motion plan
	function render_motion_plan( motion_plan=[] ) {
		$('.motion_plan_wrapper').html();
		if (motion_plan.length > 0){
			motion_plan.forEach(function( pos, index ) {
				var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-circle"><circle cx="12" cy="12" r="10"></circle></svg>';
				if (pos.turn == "_left") {
					svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-left-circle"><circle cx="12" cy="12" r="10"></circle><polyline points="12 8 8 12 12 16"></polyline><line x1="16" y1="12" x2="8" y2="12"></line></svg>';
				} else if ( pos.turn == "_right" ) {
					svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-right-circle"><circle cx="12" cy="12" r="10"></circle><polyline points="12 16 16 12 12 8"></polyline><line x1="8" y1="12" x2="16" y2="12"></line></svg>';
				}
				$('.motion_plan_wrapper').append(`<div class="planned_path">
					<div class="path_from">${pos.from}</div>
					<div class="path_to">${pos.to}</div>
					<div class="path_distance">Distance: ${pos.distance} cm</div>
					<div class="path_angle">Angle: ${pos.angle} degree (${pos.turn})</div>
					<div class="path_turn">${svg}</div>
					</div>`)
			});
		}
	}

	function random_color() {
		return Math.random() * ( 255 - 0 ) + 0;
	}

	// set robot position
	function set_robot_goals( map_id, data ) {
		postReq("/set_robot_goals", data, function(resp) {
			if( resp.success ) {
				var path = resp.path;
				if( path.length > 0 ) {

					var color1 = random_color();
					var color2 = random_color();
					var color3 = random_color();
					solution_path.marker.line.color=`rgba(${color1}, ${color2}, ${color3}, 0.41 )`;
					console.log( solution_path.marker.line.color );

					global_map_id = map_id;
					path.forEach( function( point, index ) {
						solution['x'].push( point[0] );
						solution['y'].push( point[1] );
						solution['z'].push( 1 );
					});

					goal_points.x = goals['x'];
					goal_points.y = goals['y'];

					solution_path.x = solution['x'];
					solution_path.y = solution['y'];

					var data2 = [path_points, obstacles2, goal_points, solution_path, curr_robot_pos, new_obstacles_pos ];
					console.log( data2 );
					Plotly.newPlot( "path_map", data2, layout2 );
					//Plotly.redraw("path_map");
					plot.removeEventListener('plotly_click', on_node_click );
					plot.on('plotly_click', on_node_click );

					// render motion plan
					render_motion_plan( resp.motion );

					console.log( solution, goals )

					map_timer = setInterval( get_latest_status, 5000 );
				}
			} else {
				console.error( resp );
			}
		});
	}

	// submit start and goal point
	$(document).on('click', '[data-action]', function() {
		if (goals == undefined) {
			return;
		}

		var map_id = $(this).data('map-id');
		global_end_goal   = [ goals['x'][1], goals['y'][1] ];

		var data = {
			'startx': goals['x'][0],
			'starty': goals['y'][0],
			'endx'  : goals['x'][1],
			'endy'  : goals['y'][1],
			'map_id': map_id,
			'reset_obstacles': 1,
		}

		// set robot goals and plan the motion
		set_robot_goals( map_id, data );
	});
})(jQuery);
