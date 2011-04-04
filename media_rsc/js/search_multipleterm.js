$(function() {
                
    function split(val) {
        return val.split(/,\s*/);
    }
    function extractLast(term) {
        return split(term).pop();
    }
    
    $("#id_search_term").autocomplete({
        minLength: 1,
        delay: 0,
        source: function(request, response) {
            $.getJSON(
              "/colorific/proxy/search_suggestions/",
              {'term' : extractLast(request.term)},
               response);
        },
        search: function() {
            var term = extractLast(this.value);
            if (term.length < 2) {
                return false;
            }
        },
        focus: function( event, ui ) {
		        $( "#id_search_term" ).val( ui.item.value+ " "+ui.item.desc );
		        return false;
				},
        select: function(event, ui) {
            var terms = split( this.value );
            terms.pop();
            terms.push( ui.item.value+ " "+ui.item.desc  );
            terms.push("");
            //this.value = terms.join(", ");
						this.value = terms;
            return false;
        },
    }).data( "autocomplete" )._renderItem = function( ul, item ) {
      return $( "<li></li>" )
        .data( "item.autocomplete", item )
        .append( "<a class='search-autocomplete-item'>" + item.value + "<span id='search-autocomplete-desc'> "+item.desc +"</span> <span id='search-autocomplete-type'> "+item.type +"</span></a>" )
        .appendTo( ul );
    };
});