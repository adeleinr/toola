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
        focus: function() {
            return false;
        },
        select: function(event, ui) {
            var terms = split( this.value );
            terms.pop();
            terms.push( ui.item.value );
            terms.push("");
            this.value = terms.join(", ");
            return false;
        },
    });
});