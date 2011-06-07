
var FreebaseAutocomplete = {};

// static field
FreebaseAutocomplete.hiddenValues = [];

/* IDS Enum */
FreebaseAutocomplete._Ids = {
  'ID_TOOLIDS':'#id_toolIDs', 
  'ID_TOOLS':'#id_tools',
  'ID_TOOLBOX_NAME':'#id_toolbox_name',
  'USER_PROFILE_ID':'#user-profile-id',
  'CREATE_TOOLBOX': '#create-toolbox',
  'DIALOG_FORM':'#dialog-form'
}
/* Dont remove any element from the hidden field
* even if the user removes from the input field.
* When form is about to be submitted then remove
* from the hidden field array those elements not found
* in the input field, and serialize the array into
* the hidden field.
*/
FreebaseAutocomplete.filterItems = function (){
  
  var Ids = FreebaseAutocomplete._Ids;
  var hiddenValues = FreebaseAutocomplete.hiddenValues;
  
  /* This is to deal with cases when the user deletes
   * an element from the input field array but the
   * hidden field array remains unchanged (and outdated)
   * So go through each element in the input field array
   * (those are the elements the user decided to
   * keep). For each of these elements in the input
   * field find its match in the hidden field array
   * and create a 3rd array with the final elements
   * that look like (name, id)
   */
  // This is a list of (name,ids)
  // for each keyword selected by the user
  var resultValues = {}
  // This is the raw input field value
  var inputValues = Helper.split($(Ids.ID_TOOLS).val()) // an array
  var counter = 0;
  for (var inputValue in inputValues) {
    var foundMatch = false;  
    var input_name = '';
    var hidden_name = '';   
    input_name = $.trim(inputValues[inputValue]); 
    if( input_name != ''){
      console.log("Looking at value: "+input_name);
      for (var hiddenValue in hiddenValues) {
        hidden_name = $.trim(hiddenValues[hiddenValue][0]);
        if (input_name == hidden_name) {
          console.log( "Found in freebase. Saving "+input_name);
          resultValues[counter] = hiddenValues[hiddenValue];
          foundMatch = true;
          counter++;
        }
      }
      if ( !foundMatch ){
        var array = [];
        array[0] = input_name;
        array[1] = "";
        console.log( "Not found in freebase but Saving "+input_name)
        resultValues[counter] = array;
        counter++;
      }
    }// end if
    
  }
  $(Ids.ID_TOOLIDS).val(JSON.stringify(resultValues))
  
}


$("#id_tools")
  .suggest({
    zIndex: 2000,
    "suggest_new": "Click on me if you don't see anything in the list",

  })
  .bind("fb-select", function(e, data) {
    var array = []
    array[0] = data.name
    array[1] = data.id
    FreebaseAutocomplete.hiddenValues.push( array );
    console.log(FreebaseAutocomplete.hiddenValues)
  })
  .bind("fb-select-new", function(e, val) {
    console.log("Suggest new: " + val);
    var array = []
    array[0] = Helper.extractLast(val)
    array[1] = ""
    FreebaseAutocomplete.hiddenValues.push( array );
    console.log(FreebaseAutocomplete.hiddenValues)
  });

  var FreebaseModalBox = function(){  

    var Ids = FreebaseAutocomplete._Ids;
    this.toolbox_name = $( Ids.ID_TOOLBOX_NAME );          // Instance var
    this.tools = $( Ids.ID_TOOLS );                        
   this.tips = $( ".validateTips" );                      
   this.userProfile_id = $( Ids.USER_PROFILE_ID ).val(); 
    this.createDialogWindow();
    this.openDialogWindow();
    
  }
                           

  FreebaseModalBox.prototype.createDialogWindow = function(){
         
    var Ids = FreebaseAutocomplete._Ids; // Local var
    var that = this;
    var allFields = $( [] ).add( this.toolbox_name ).add( this.tools );
        
    $( Ids.DIALOG_FORM ).dialog({
        draggable: false,
        resizable: false,
        autoOpen: false,
        height: 300,
        width: 430,
        modal: true,
        buttons: {
            "Create a toolbox": function() {
            var bValid = true;
            allFields.removeClass( "ui-state-error" );
  
            bValid = bValid && that.checkLength( that.toolbox_name, "Toolbox Name", 1, 500 );
            bValid = bValid && that.checkLength( that.tools,"Tool", 1, 500 );
            
            if ( bValid ) {
              // Cleanup for Freebase suggest
              FreebaseAutocomplete.filterItems()
              // filterItems() should have populated this hidden field
              var tools_filtered = $(Ids.ID_TOOLIDS);
              console.log(tools_filtered.val())
              
              $.ajax({ 
                  url: 'http://HOST_IP_TAG/colorific/proxy/toolbox/',
                  type: "GET",
                  data: 'toolbox_name=' + that.toolbox_name.val()+
                        '&tools=' + tools_filtered.val() +
                        '&userprofile_id=' + that.userProfile_id,
                  success: function(data) {
                      $( Ids.DIALOG_FORM ).dialog( "close" );
                      // Force cache to expire and reload page
                      window.location.reload();
                  },
                  error: function(obj, a, b) {
                      console.log(obj.status + " => " + obj.statusText)
                  }
              });
              
  
            }
          },
          Cancel: function() {
            $( this ).dialog( "close" );
          }
        },
        close: function() {
          allFields.val( "" ).removeClass( "ui-state-error" );
        }
      });
    
    
  }
  
  FreebaseModalBox.prototype.openDialogWindow = function(){
    var Ids = FreebaseAutocomplete._Ids;
    $( Ids.CREATE_TOOLBOX )
      .button()
      .click(function() {
        $( Ids.DIALOG_FORM ).dialog( "open" );
    });
  
  }
  
  FreebaseModalBox.prototype.updateTips = function ( t ){ 
    this.tips
     .text( t )
     .addClass( "ui-state-highlight" );
   setTimeout(function() {
     tips.removeClass( "ui-state-highlight", 1500 );
   }, 500 );  
  }
  
  FreebaseModalBox.prototype.checkLength = function ( o, n, min, max ){
    if ( o.val().length > max || o.val().length < min ) {
     o.addClass( "ui-state-error" );
     if (min > 1){
       this.updateTips( "You need at least " + min + " " + n +" , and max "+max);
     }else{
       this.updateTips( "You need a " + n);
     }
     return false;
   } else {
     return true;
   }
  }
  
  FreebaseModalBox.prototype.checkRegexp = function( o, regexp, n ){
    if ( !( regexp.test( o.val() ) ) ) {
     o.addClass( "ui-state-error" );
     this.updateTips( n );
     return false;
   } else {
     return true;
   }
  };
 
 /*
  FreebaseModalBox.prototype.updatelistToolbox = function() {
  
   Ids = FreebaseAutocomplete._Ids;
    
    alert($("#get-toolboxes-username").val)
    
    $.ajax({
      url: 'http://HOST_IP_TAG/colorific/proxy/toolboxes/',
      type: "GET",
      success: function(json) {
        json = $.parseJSON(json);
        
        var toolboxesList = [];
        for (key in json) {
          var toolList = [];
          toolboxesList.push('<div class="clickable span-15 last"id="toolboxTab"  url="{{toolBox.absolute_url}}">');
          toolboxesList.push('<div id="main" class="span-15 last">');
          toolboxesList.push('<div id="tools" class="span-12">');
          toolboxesList.push('<h5>{{toolBox.toolbox_name}}'+
                                  '<span id="author"> '+
                                  '<a href="{{toolBox.user.absolute_url}}"> by+ {{toolBox.user.user.username}}</a></span></h5>')';
          toolboxesList.push('<br />');
          toolboxesList.push('TIGS');
          toolboxesList.push('</div>');
          toolboxesList.push('<div id="toolbox" class="span-11 last">')
          toolboxesList.push('<span class="toolBoxTitleSmall">'+ json[key].toolbox_name + '</span>');
          toolboxesList.push('<div>');
          for (key2 in json[key].tools) {
            toolList.push(json[key].tools[key2].tool_name);
          }
          toolboxesList.push(toolList.join(', '));
          toolboxesList.push('</div>');
          toolboxesList.push('</div>');
          toolboxesList.push('</div>');
        }
        
        var results = document.createElement('div');
        results.innerHTML = toolboxesList.join('');
        $('#toolboxes')[0].innerHTML = ''
        $('#toolboxes')[0].appendChild(results);
        $('#toolboxes')[0].fadeIn("slow");
      },
      error: function(obj) {
        alert(obj.status + " => " + obj.statusText)
      }
    });
  }
  */
  
  new FreebaseModalBox();
