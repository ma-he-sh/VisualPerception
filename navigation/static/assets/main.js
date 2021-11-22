(function($) {
    console.log( 'server loaded' );
    
    function show_message( _id, message='' ) {
        $( `[data-status="${_id}"]` ).text( message );
    }

    function rest( url, method, data, success_callback, error_callback ) {
        $.ajax({
            url: url,
            type: method,
            data: data,
            contentType: false,
            processData: false,
            success: function(resp) {
                success_callback(resp)
            },
            error: function(err) {
                error_callback(err)
            }
        });
    }

    function postReq( url, data, callback ) {
        $.post( url, data, callback );
    }

    function getReq( url, data, callback ) {
        $.get( url, data, callback );
    }

    function reload_maps() {
        rest( '/get_maps', 'get', {}, function( resp ) {
            console.log(resp);
        }, function( err ) {
            console.log( err );
        });
    }

    function delete_map( file_uuid ) {
        postReq( '/delete_map', {
            'file_uuid': file_uuid
        }, function( resp ) {
            location.reload()
        } );
    }

    function view_map( file_uuid ) {
        getReq( '/get_map_url', {
            'file_uuid': file_uuid,
        }, function( resp ) {
            if (resp.success) {
                var img = new Image()
                img.src = resp.url;
                img.onload = function() {
                    $('#preview_map').empty().append( img );
                    $('.app_preview_wrapper').removeClass('hidden_wrapper');
                }
                img.onerror = function() {
                    $('#preview_map').empty().html('');
                    $('.app_preview_wrapper').addClass('hidden_wrapper');
                }
                 $('#preview_map').empty().html('LOADING');
            }
        } );
    }

    $( '#upload_btn' ).on( 'click', function() {
        var fileData = new FormData( $('form#map_upload')[0] );

        var map_width = $("input[name='map_width']").val();
        var map_height= $("input[name='map_height']").val();

        fileData.append( "map_width", map_width );
        fileData.append( "map_height", map_height );

        $.ajax({
            url: '/upload_map',
            type: 'post',
            data: fileData,
            contentType: false,
            processData: false,
            success: function( resp ) {
                show_message( 'prompt_upload_status', resp.message );
                if (!resp.error) {
                    location.reload()
                }
            },
            error: function( err ) {
                console.log( err );
            }
        })
    });

    // handle toggling the sections
    $(document).on('click', '[data-toggle-id]', function() {
        var section_id = $(this).data('toggle-id');
        var section_wrapper = $( `[data-toggle-wrapper="${section_id}"]` );
        if( section_wrapper.length > 0 ) {
            if( section_wrapper.hasClass('hidden_section') ) {
                section_wrapper.removeClass('hidden_section')
            } else {
                section_wrapper.addClass('hidden_section')
            }
        }
    });

    // handle actions
    $(document).on('click', '[data-action]', function() {
        var action_id = $(this).data('action');
        var map_id = $(this).data('map-id');

        switch( action_id ) {
            case 'play':
                window.location.href='/run_map=' + map_id;
                break;
            case 'view':
                view_map( map_id );
                break;
            case 'trash':
                delete_map( map_id );
                break;
        }
    });

    // close the preview
    $(document).on('click', '[data-close-btn]', function() {
        $('.app_preview_wrapper').addClass('hidden_wrapper');
    });
})(jQuery);
