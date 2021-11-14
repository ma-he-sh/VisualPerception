(function($) {
    console.log( 'server loaded' );
    
    function show_message( _id, message='' ) {
        $( `[data-status="${_id}"]` ).text( message );
    }

    function reload_maps() {
        $.ajax({
            url: '/get_maps',
            type: 'get',
            contentType: 'application/json',
            success: function(resp){
                console.log( resp )
            },
            error: function( err ) {
                console.log( err )
            }
        })
    }

    $( '#upload_btn' ).on( 'click', function() {
        var fileData = new FormData( $('form#map_upload')[0] );

        $.ajax({
            url: '/upload_map',
            type: 'post',
            data: fileData,
            contentType: false,
            processData: false,
            success: function( resp ) {
                console.log( resp );
                show_message( 'prompt_upload_status', resp.message );
                if (!resp.error) {
                    reload_maps();
                }
            },
            error: function( err ) {
                console.log( err );
            }
        })
    });
})(jQuery);
