$(function() {
    //console.log($(".test").length);
    //console.log($(".test:eq(0)").attr('test'));
    for(var i = 0; i < $(".filename").length; i++) {
        $(".filename:eq(" + i + ")").change(function(){
            var filenames = [];
            var nof = 0;
            //console.log($(this).prop('checked'));
            //console.log($(".test").length);
            for(var g = 0; g < $(".filename").length; g++) {
                //console.log($(".test:eq(" + g + ")").prop('checked'));
                if($(".filename:eq(" + g + ")").prop('checked')) {
                    //console.log($(".test:eq(" + g + ")").attr('test'));
                    filenames.push($(".filename:eq(" + g + ")").attr('filename'));
                    nof++;
                }
            }
            console.log(filenames);
            //getData(filenames, nof);
            printMarkers(filenames, nof);
        });
    }
});