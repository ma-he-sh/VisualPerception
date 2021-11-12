(function($) {
    console.log( 'server loaded' );
    
    function show_message( _id, message='' ) {
        $( `[data-status="${_id}"]` ).text( message );
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
            },
            error: function( err ) {
                console.log( err );
            }
        })
    });
})(jQuery);
