/******************************************************************************
 * All source and examples in this project are subject to the
 * following copyright, unless specifically stated otherwise
 * in the file itself:
 *
 * Copyright (c) 2007-2009, Metaweb Technologies, Inc.
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 *       copyright notice, this list of conditions and the following
 *       disclaimer in the documentation and/or other materials provided
 *       with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY METAWEB TECHNOLOGIES ``AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL METAWEB TECHNOLOGIES BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 * BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
 * IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *****************************************************************************/
 
 
(function($, undefined){

    /* Added by Adelein */
    function split(val) {
      return val.split(/,\s*/);
		}
		function extractLast(term) {
		  return split(term).pop();
		}
    /* Added by Adelein */
		
     if (!("console" in window)) {
         var c = window.console = {};
         c.log = c.warn = c.error = c.debug = function(){};
     }

     /**
      * jQuery UI provides a way to be notified when an element is removed from the DOM.
      * suggest would like to use this facility to properly teardown it's elements from the DOM (suggest list, flyout, etc.).
      * The following logic tries to determine if "remove" event is already present, else
      * tries to mimic what jQuery UI does (as of 1.8.5) by adding a hook to $.cleanData or $.fn.remove.
      */
     $(function() {
         var div = $("<div>");
         $(document.body).append(div);
         var t = setTimeout(function() {
           // copied from jquery-ui
           // for remove event
           if ( $.cleanData ) {
             var _cleanData = $.cleanData;
             $.cleanData = function( elems ) {
               for ( var i = 0, elem; (elem = elems[i]) != null; i++ ) {
                 $( elem ).triggerHandler( "remove" );
               }
               _cleanData( elems );
             };
           } else {
             var _remove = $.fn.remove;
             $.fn.remove = function( selector, keepData ) {
               return this.each(function() {
                 if ( !keepData ) {
                   if ( !selector || $.filter( selector, [ this ] ).length ) {
                     $( "*", this ).add( [ this ] ).each(function() {
                       $( this ).triggerHandler( "remove" );
                     });
                   }
                 }
                 return _remove.call( $(this), selector, keepData );
               });
             };
           }
         },1);
         div.bind("remove", function() {
           clearTimeout(t);
         });
         div.remove();
     });

     $.suggest = function(name, prototype) {

         $.fn[name] = function(options) {
             if (!this.length) {
                 console.warn('Suggest: invoked on empty element set');
             }
             return this
                 .each(function() {
                           if (this.nodeName) {
                               if (this.nodeName.toUpperCase() === 'INPUT') {
                                   if (this.type &&
                                       this.type.toUpperCase() !== 'TEXT') {
                                       console.warn('Suggest: unsupported INPUT type: '+this.type);
                                   }
                               }
                               else {
                                   console.warn('Suggest: unsupported DOM element: '+this.nodeName);
                               }
                           }
                           var instance = $.data(this, name);
                           if (instance) {
                               instance._destroy();
                           }
                           $.data(this, name,
                                  new $.suggest[name](this, options))._init();
                       });
         };


         $.suggest[name] = function(input, options) {

             var self = this,
             o = this.options = $.extend(true, {},
                                         $.suggest.defaults,
                                         $.suggest[name].defaults,
                                         options),
             p = o.css_prefix = o.css_prefix || "",
             css = o.css;

             this.name = name;

             $.each(css, function(k, v) {
                        css[k] = p + css[k];
                    });

             // suggest parameters
             o.ac_param = {};
             $.each(["type", "type_strict", "mql_filter",
                     "as_of_time", "exclude_guids", "category", "all_types"],
                    function(i,n) {
                        var v = o[n];
                        if (v === null || v === "") {
                            return;
                        }
                        if (typeof v === "object") {
                            v = JSON.stringify(v);
                        }
                        o.ac_param[n] = v;
                    });
             if (o.ac_param.type) {
                 this.options._type = $.map(o.ac_param.type.split(/[, ]/),
                                            function(n, i) {
                                                return n.replace(/[\"\[\]]/g, "");
                                            });
             };

             // status texts
             this._status = {
                 START: "",
                 LOADING: "",
                 SELECT: "",
                 ERROR: ""
             };
             if (o.status && o.status instanceof Array && o.status.length >= 3) {
                 this._status.START = o.status[0] || "";
                 this._status.LOADING = o.status[1] || "";
                 this._status.SELECT = o.status[2] || "";
                 if (o.status.length === 4) {
                     this._status.ERROR = o.status[3] || "";
                 }
             }

             // create the container for the drop down list
             var s = this.status = $('<div style="display:none;">')
                 .addClass(css.status),
             l = this.list = $("<ul>").addClass(css.list),
             p = this.pane = $('<div style="display:none;" class="fbs-reset">')
                 .addClass(css.pane);

             p.append(s).append(l);

             if (o.parent) {
                 $(o.parent).append(p);
             }
             else {
                 p.css("position","absolute");
                 if (o.zIndex) {
                     p.css("z-index", o.zIndex);
                 }
                 $(document.body).append(p);
             }
             p.bind("mousedown", function(e) {
                        //console.log("pane mousedown");
                        self.input.data("dont_hide", true);
                        e.stopPropagation();
                    })
                 .bind("mouseup", function(e) {
                           //console.log("pane mouseup");
                           if (self.input.data("dont_hide")) {
                               self.input.focus();
                           }
                           self.input.removeData("dont_hide");
                           e.stopPropagation();
                       })
                 .bind("click", function(e) {
                           //console.log("pane click");
                           e.stopPropagation();
                           var s = self.get_selected();
                           if (s) {
                               self.onselect(s, true);
                               self.hide_all();
                           }
                       });

             var hoverover = function(e) {
                 self.hoverover_list(e);
             };
             var hoverout = function(e) {
                 self.hoverout_list(e);
             };
             l.hover(hoverover, hoverout);


             //console.log(this.pane, this.list);

             this.input = $(input)
                 .attr("autocomplete", "off")
                 .unbind(".suggest")
                 .bind("remove.suggest", function(e) {
                     self._destroy();
                 })
                 .bind("keydown.suggest", function(e) {
                           self.keydown(e);
                       })
                 .bind("keypress.suggest", function(e) {
                           self.keypress(e);
                       })
                 .bind("keyup.suggest", function(e) {
                           self.keyup(e);
                       })
                 .bind("blur.suggest", function(e) {
                           self.blur(e);
                       })
                 .bind("textchange.suggest", function(e) {
                           self.textchange();
                       })
                 .bind("focus.suggest", function(e) {
                           self.focus(e);
                       })
                 .bind($.browser.msie ? "paste.suggest" : "input.suggest",
                       function(e) {
                           clearTimeout(self.paste_timeout);
                           self.paste_timeout = setTimeout(function() {
                                                               self.textchange();
                                                           }, 0);
                       });

             // resize handler
             this.onresize = function(e) {
                 self.invalidate_position();
                 if (p.is(":visible")) {
                     self.position();
                     if (o.flyout && self.flyoutpane &&
                         self.flyoutpane.is(":visible")) {
                         var s = self.get_selected();
                         if (s) {
                             self.flyout_position(s);
                         }
                     }
                 }
             };

             $(window)
                 .bind("resize.suggest", this.onresize)
                 .bind("scroll.suggest", this.onresize);
         };

         $.suggest[name].prototype = $.extend({}, $.suggest.prototype, prototype);
     };

     // base suggest prototype
     $.suggest.prototype = {

         _init: function() {},

         _destroy: function() {
             this.pane.remove();
             this.list.remove();
             this.input.unbind(".suggest");
             $(window).unbind("resize.suggest", this.onresize)
                 .unbind("scroll.suggest", this.onresize);
             this.input.removeData("data.suggest");
         },

         invalidate_position: function() {
             self._position = null;
         },

         status_start: function() {
             this.hide_all();
             this.status.siblings().hide();
             if (this._status.START) {
                 this.status.text(this._status.START).show();
                 if (!this.pane.is(":visible")) {
                     this.position();
                     this.pane_show();
                 }
             }
             if (this._status.LOADING) {
                 this.status.removeClass("loading");
             }
         },

         status_loading: function() {
             this.status.siblings().show();

             if (this._status.LOADING) {
                 this.status.addClass("loading")
                     .text(this._status.LOADING).show();
                 if (!this.pane.is(":visible")) {
                     this.position();
                     this.pane_show();
                 }
             }
             else {
                 this.status.hide();
             }
         },

         status_select: function() {
             this.status.siblings().show();
             if (this._status.SELECT) {
                 this.status.text(this._status.SELECT).show();
             }
             else {
                 this.status.hide();
             }
             if (this._status.LOADING) {
                 this.status.removeClass("loading");
             }
         },

         status_error: function() {
             this.status.siblings().show();
             if (this._status.ERROR) {
                 this.status.text(this._status.ERROR).show();
             }
             else {
                 this.status.hide();
             }
             if (this._status.LOADING) {
                 this.status.removeClass("loading");
             }
         },

         focus: function(e) {
             //console.log("focus", this.input.val() === "");
             var o = this.options,
             v = this.input.val();
             if (v === "") {
                 this.status_start();
             }
             else {
                 this.focus_hook(e);
             }
         },

         // override to be notified on focus and input has a value
         focus_hook: function(e) {
             //console.log("focus_hook", this.input.data("data.suggest"));
             if (!this.input.data("data.suggest") &&
                 !this.pane.is(":visible") &&
                 $("." + this.options.css.item, this.list).length) {
                 this.position();
                 this.pane_show();
             }
         },

         keydown: function(e) {
             var key = e.keyCode;
             if (key === 9) { // tab
                 this.tab(e);
             }
             else if (key === 38 || key === 40) { // up/down
                 if (!e.shiftKey) {
                     // prevents cursor/caret from moving (in Safari)
                     e.preventDefault();
                 }
             }
         },

         keypress: function(e) {
             var key = e.keyCode;
             if (key === 38 || key === 40) { // up/down
                 if (!e.shiftKey) {
                     // prevents cursor/caret from moving
                     e.preventDefault();
                 }
             }
             else if (key === 13) { // enter
                 this.enter(e);
             }
         },

         keyup: function(e) {
             var key = e.keyCode;
             //console.log("keyup", key);
             if (key === 38) { // up
                 e.preventDefault();
                 this.up(e);
             }
             else if (key === 40) { // down
                 e.preventDefault();
                 this.down(e);
             }
             else if (e.ctrlKey && key === 77) {
                 $(".fbs-more-link", this.pane).click();
             }

             else if ($.suggest.is_char(e)) {
                 //this.textchange();
                 clearTimeout(this.keypress.timeout);
                 var self = this;
                 this.keypress.timeout = setTimeout(function() {
                                                        self.textchange();
                                                    }, 0);
             }
             else if (key === 27) {
                 // escape - WebKit doesn't fire keypress for escape
                 this.escape(e);
             }

             return true;
         },

         blur: function(e) {
             //console.log("blur", "dont_hide", this.input.data("dont_hide"),
             //            "data.suggest", this.input.data("data.suggest"));
             if (this.input.data("dont_hide")) {
                 return;
             }
             var data = this.input.data("data.suggest");
             if (!data) {
                 this.check_required(e);
             }
             this.hide_all();
         },

         tab: function(e) {
             if (e.shiftKey || e.metaKey || e.ctrlKey) {
                 return;
             }

             var o = this.options,
             visible = this.pane.is(":visible") &&
                 $("." + o.css.item, this.list).length,
             s = this.get_selected();

             //console.log("tab", visible, s);

             if (visible && s) {
                 this.onselect(s);
                 this.hide_all();
             }
         },

         enter: function(e) {
             var o = this.options,
             visible = this.pane.is(":visible");

             //console.log("enter", visible);

             if (visible) {
                 if (e.shiftKey) {
                     this.shift_enter(e);
                     e.preventDefault();
                 }
                 else if ($("." + o.css.item, this.list).length) {
                     var s = this.get_selected();
                     if (s) {
                         this.onselect(s);
                         this.hide_all();
                         e.preventDefault();
                     }
                     else {
                         var data = this.input.data("data.suggest");
                         if (o.soft) {
                             if (!data) {
                                 this.check_required(e);
                             }
                         }
                         else {
                             if ($("."+this.options.css.item + ":visible",
                                   this.list).length) {
                                 this.updown(false);
                                 e.preventDefault();
                             }
                             else if (!data) {
                                 this.check_required(e);
                             }
                         }
                     }
                 }
                 //console.log("enter preventDefault");
             }
         },

         shift_enter: function(e) {},

         escape: function(e) {
             this.hide_all();
         },

         up: function(e) {
             //console.log("up");
             this.updown(true, e.ctrlKey || e.shiftKey);
         },

         down: function(e) {
             //console.log("up");
             this.updown(false, null, e.ctrlKey || e.shiftKey);
         },

         updown: function(goup, gofirst, golast) {
             //console.log("updown", goup, gofirst, golast);
             var o = this.options,
             css = o.css,
             p = this.pane,
             l = this.list;

             if (!p.is(":visible")) {
                 if (!goup) {
                     this.textchange();
                 }
                 return;
             }
             var li = $("."+css.item + ":visible", l);

             if (!li.length) {
                 return;
             }

             var first = $(li[0]),
             last = $(li[li.length-1]),
             cur = this.get_selected() || [];

             clearTimeout(this.ignore_mouseover.timeout);
             this._ignore_mouseover = false;

             if (goup) {//up
                 if (gofirst) {
                     this._goto(first);
                 }
                 else if (!cur.length) {
                     this._goto(last);
                 }
                 else if (cur[0] == first[0]) {
                     first.removeClass(css.selected);
                     this.input.val(this.input.data("original.suggest"));
                     this.hoverout_list();
                 }
                 else {
                     var prev = cur.prevAll("."+css.item + ":visible:first");
                     this._goto(prev);
                 }
             }
             else {//down
                 if (golast) {
                     this._goto(last);
                 }
                 else if (!cur.length) {
                     this._goto(first);
                 }
                 else if (cur[0] == last[0]) {
                     last.removeClass(css.selected);
                     this.input.val(this.input.data("original.suggest"));
                     this.hoverout_list();
                 }
                 else {
                     var next = cur.nextAll("."+css.item + ":visible:first");
                     this._goto(next);
                 }
             }
         },

         _goto: function(li) {
             li.trigger("mouseover.suggest");
             var d = li.data("data.suggest");
             this.input.val(d ? d.name : this.input.data("original.suggest"));
             this.scroll_to(li);
         },

         scroll_to: function(item) {
             var l = this.list,
             scrollTop = l.scrollTop(),
             scrollBottom = scrollTop + l.innerHeight(),
             item_height = item.outerHeight(),
             offsetTop = item.prevAll().length * item_height,
             offsetBottom = offsetTop + item_height;
             if (offsetTop < scrollTop) {
                 this.ignore_mouseover();
                 l.scrollTop(offsetTop);
             }
             else if (offsetBottom > scrollBottom) {
                 this.ignore_mouseover();
                 l.scrollTop(scrollTop + offsetBottom - scrollBottom);
             }
         },

         textchange: function() {
             this.input.removeData("data.suggest");
             this.input.trigger("fb-textchange", this);
             var v = this.input.val();
             if (v === "") {
                 this.status_start();
                 return;
             }
             else {
                 this.status_loading();
             }
             this.request(v);
         },

         request: function() {},

         response: function(data) {
             if (!data) {
                 return;
             }
             if ("cost" in data) {
                 this.trackEvent(this.name, "response", "cost", data.cost);
             }

             if (!this.check_response(data)) {
                 return;
             }
             var result = [];

             if ($.isArray(data)) {
                 result = data;
             }
             else if ("result" in data) {
                 result = data.result;
             }

             var args = $.map(arguments, function(a) {
                                  return a;
                              });

             this.response_hook.apply(this, args);

             var first = null,
             self = this,
             o = this.options;

             $.each(result, function(i,n) {
                        var li = self.create_item(n, data)
                            .bind("mouseover.suggest", function(e) {
                                      self.mouseover_item(e);
                                  })
                            .data("data.suggest", n);
                        self.list.append(li);
                        if (i === 0) {
                            first = li;
                        }
                    });

             this.input.data("original.suggest", this.input.val());


             if ($("."+o.css.item, this.list).length === 0 && o.nomatch) {
                 var $nomatch = $('<li class="fbs-nomatch">').html(o.nomatch)
                     .bind("click.suggest", function(e) {
                               e.stopPropagation();
                               //                    self.input.focus();
                           });
                 this.list.append($nomatch);
             }

             args.push(first);
             this.show_hook.apply(this, args);
             this.position();
             this.pane_show();
         },

         pane_show: function() {
             var show = false;
             if ($("> li", this.list).length) {
                 show = true;
             }
             if (!show) {
                 this.pane.children(":not(." + this.options.css.list + ")")
                     .each(function() {
                               if ($(this).css("display") != "none") {
                                   show = true;
                                   return false;
                               }
                           });
             }
             if (show) {
                 if (this.options.animate) {
                     var self = this;
                     this.pane.slideDown("fast", function() {
                                             self.input.
                                                 trigger("fb-pane-show", self);
                                         });
                 }
                 else {
                     this.pane.show();
                     this.input.trigger("fb-pane-show", this);
                 }

             }
             else {
                 this.pane.hide();
                 this.input.trigger("fb-pane-hide", this);
             }
         },

         create_item: function(data, response_data) {
             var css = this.options.css;
             li = $("<li>").addClass(css.item);
             var label = $("<label>").text(data.name);
             data.name = label.text();
             li.append($("<div>").addClass(css.item_name).append(label));
             return li;
         },

         mouseover_item: function(e) {
             if (this._ignore_mouseover) {
                 return;
             }
             var target = e.target;
             if (target.nodeName.toLowerCase() !== "li") {
                 target = $(target).parents("li:first");
             }
             var li = $(target),
             css = this.options.css,
             l = this.list;
             $("."+css.item, l)
                 .each(function() {
                           if (this !== li[0]) {
                               $(this).removeClass(css.selected);
                           }
                       });
             if (!li.hasClass(css.selected)) {
                 li.addClass(css.selected);
                 this.mouseover_item_hook(li);
             }
         },

         mouseover_item_hook: function($li) {},

         hoverover_list: function(e) {},

         hoverout_list: function(e) {},

         check_response: function(response_data) {
             return true;
         },

         response_hook: function(response_data) {
             //this.pane.hide();
             this.list.empty();
         },

         show_hook: function(response_data) {
             // remove anything next to list - added by other suggest plugins
             this.status_select();
         },

         position: function() {
             var p  = this.pane,
             o = this.options;

             if (o.parent) {
                 return;
             }

             if (!self._position) {
                 var inp = this.input,
                 pos = inp.offset(),
                 input_width = inp.outerWidth(true),
                 input_height = inp.outerHeight(true);
                 pos.top += input_height;

                 // show to calc dimensions
                 var pane_width = p.outerWidth(),
                 pane_height = p.outerHeight(),
                 pane_right = pos.left + pane_width,
                 pane_bottom = pos.top + pane_height,
                 pane_half = pos.top + pane_height / 2,
                 scroll_left =  $(window).scrollLeft(),
                 scroll_top =  $(window).scrollTop(),
                 window_width = $(window).width(),
                 window_height = $(window).height(),
                 window_right = window_width + scroll_left,
                 window_bottom = window_height + scroll_top;


                 // is input left or right side of window?
                 var left = true;
                 if ('left' == o.align ) {
                     left = true;
                 }
                 else if ('right' == o.align ) {
                     left = false;
                 }
                 else if (pos.left > (scroll_left + window_width/2)) {
                     left = false;
                 }
                 if (!left) {
                     left = pos.left - (pane_width - input_width);
                     if (left > scroll_left) {
                         pos.left = left;
                     }
                 }

                 if (pane_half > window_bottom) {
                     // can we see at least half of the list?
                     var top = pos.top - input_height - pane_height;
                     if (top > scroll_top) {
                         pos.top = top;
                     }
                 }
                 this._position = pos;
             }
             p.css({top:this._position.top, left:this._position.left});
         },

         ignore_mouseover: function(e) {
             this._ignore_mouseover = true;
             var self = this;
             this.ignore_mouseover.timeout =
                 setTimeout(function() {
                                self.ignore_mouseover_reset();
                            }, 1000);
         },

         ignore_mouseover_reset: function() {
             this._ignore_mouseover = false;
         },

         get_selected: function() {
             var selected = null,
             select_class = this.options.css.selected;
             $("li", this.list)
                 .each(function() {
                           var $this = $(this);
                           if ($this.hasClass(select_class) &&
                               $this.is(":visible")) {
                               selected = $this;
                               return false;
                           }
                       });
             return selected;
         },

         onselect: function($selected, focus) {
				 	
					   /* Added by Adelein */
						 var terms = split(this.input[0].value);
						 terms.pop();
						 terms.push($selected.data("data.suggest").name);
						 var concatenated_selections = terms.join(", ");
						 /* Added by Adelein */
						
						 var data = $selected.data("data.suggest")

             if (data) {
                 this.input.val(concatenated_selections)
                     .data("data.suggest", data)
                     .trigger("fb-select", data);

                 this.trackEvent(this.name, "fb-select", "index",
                                 $selected.prevAll().length);
             }
					
             /*
             else {
                 //this.check_required();
             }
             if (focus) {
                 //          this.input.focus();
             }
              */
         },

         trackEvent: function(category, action, label, value) {
             this.input.trigger("fb-track-event", {
                                    category: category,
                                    action:action,
                                    label: label,
                                    value: value
                                });
             //console.log("trackEvent", category, action, label, value);
         },

         check_required: function(e) {
             var required = this.options.required;
             if (required === true) {
                 var v = this.input.val();
                 if (v !== "") {
                     this.input.trigger("fb-required", {domEvent:e});
                     return false;
                 }
             }
             else if (required === "always") {
                 this.input.trigger("fb-required", {domEvent:e});
                 return false;
             }
             return true;
         },

         hide_all: function(e) {
             this.pane.hide();
             this.input.trigger("fb-pane-hide", this);
         }

     };


     $.extend($.suggest, {

                  defaults: {

                      status: ['Start typing to get suggestions...',
                               'Searching...',
                               'Select an item from the list:',
                               'Sorry, something went wrong. Please try again later'],

                      required: false,

                      soft: false,

                      nomatch: "no matches",

                      // CSS default class names
                      css: {
                          pane: "fbs-pane",
                          list: "fbs-list",
                          item: "fbs-item",
                          item_name: "fbs-item-name",
                          selected: "fbs-selected",
                          status: "fbs-status"
                      },

                      css_prefix: null,

                      parent: null,

                      // option to animate suggest list when shown
                      animate: false,

                      zIndex: null
                  },

                  $$: function(cls, ctx) {
                      /**
                       * helper for class selector
                       */
                      return $("." + cls, ctx);
                  },

                  use_jsonp: function(service_url) {
                      /*
                       * if we're on the same host,
                       * then we don't need to use jsonp.
                       * This greatly increases our cachability
                       */
                      if (!service_url) {
                          return false; // no host == same host == no jsonp
                      }

                      var pathname_len = window.location.pathname.length;
                      var hostname = window.location.href;
                      hostname = hostname.substr(0, hostname.length -
                                                 pathname_len);
                      //console.log("Hostname = ", hostname);
                      if (hostname === service_url) {
                          return false;
                      }
                      return true;
                  },

                  strongify: function(str, substr) {
                      // safely markup substr within str with <strong>
                      var strong = str;
                      var index = str.toLowerCase().indexOf(substr.toLowerCase());
                      if (index >= 0) {
                          var substr_len = substr.length;
                          strong = $("<div>").text(str.substring(0, index))
                              .append($("<strong>").text(str.substring(index, index + substr_len)))
                              .append(document.createTextNode(str.substring(index + substr_len)))
                              .html();
                      }
                      return strong;
                  },

                  keyCode: {
                      //BACKSPACE: 8,
                      CAPS_LOCK: 20,
                      //COMMA: 188,
                      CONTROL: 17,
                      //DELETE: 46,
                      DOWN: 40,
                      END: 35,
                      ENTER: 13,
                      ESCAPE: 27,
                      HOME: 36,
                      INSERT: 45,
                      LEFT: 37,
                      //NUMPAD_ADD: 107,
                      //NUMPAD_DECIMAL: 110,
                      //NUMPAD_DIVIDE: 111,
                      NUMPAD_ENTER: 108,
                      //NUMPAD_MULTIPLY: 106,
                      //NUMPAD_SUBTRACT: 109,
                      PAGE_DOWN: 34,
                      PAGE_UP: 33,
                      //PERIOD: 190,
                      RIGHT: 39,
                      SHIFT: 16,
                      SPACE: 32,
                      TAB: 9,
                      UP: 38,
                      OPTION: 18,
                      APPLE: 224
                  },

                  is_char: function(e) {
                      if (e.type === "keypress") {
                          if ((e.metaKey || e.ctrlKey) && e.charCode === 118) {
                              // ctrl+v
                              return true;
                          }
                          else if ("isChar" in e) {
                              return e.isChar;
                          }
                      }
                      else {
                          var not_char = $.suggest.keyCode.not_char;
                          if (!not_char) {
                              not_char = {};
                              $.each($.suggest.keyCode, function(k,v) {
                                         not_char[''+v] = 1;
                                     });
                              $.suggest.keyCode.not_char = not_char;
                          }
                          return !(('' + e.keyCode) in not_char);
                      }
                  }
              });


     // some base implementation that we overwrite but want to call
     var base = {
         _destroy: $.suggest.prototype._destroy,
         show_hook: $.suggest.prototype.show_hook
     };


     // *THE* Freebase suggest implementation
     $.suggest("suggest", {
                   _init: function() {
                       var self = this,
                       o = this.options;
                       if (!o.flyout_service_url) {
                           o.flyout_service_url = o.service_url;
                       }
                       this.jsonp = $.suggest.use_jsonp(o.service_url);

                       if (!$.suggest.cache) {
                           $.suggest.cache = {};
                       }

                       if (o.flyout) {
                           this.flyoutpane = $('<div style="display:none;" class="fbs-reset">').addClass(o.css.flyoutpane);

                           if (o.flyout_parent) {
                               $(o.flyout_parent).append(this.flyoutpane);
                           }
                           else {
                               this.flyoutpane.css("position","absolute");
                               if (o.zIndex) {
                                   this.flyoutpane.css("z-index", o.zIndex);
                               }
                               $(document.body).append(this.flyoutpane);
                           }
                           var hoverover = function(e) {
                               self.hoverover_list(e);
                           };
                           var hoverout = function(e) {
                               self.hoverout_list(e);
                           };
                           this.flyoutpane.hover(hoverover, hoverout)
                               .bind("mousedown.suggest", function(e) {
                                         e.stopPropagation();
                                         self.pane.click();
                                     });

                           if (!$.suggest.flyout) {
                               $.suggest.flyout = {};
                           }
                           if (!$.suggest.flyout.cache) {
                               $.suggest.flyout.cache = {};
                           }
                       }
                   },

                   _destroy: function() {
                       base._destroy.call(this);
                       if (this.flyoutpane) {
                           this.flyoutpane.remove();
                       }
                       this.input.removeData("request.count.suggest");
                       this.input.removeData("flyout.request.count.suggest");
                   },

                   shift_enter: function(e) {
                       if (this.options.suggest_new) {
                           this.suggest_new();
                           this.hide_all();
                       }
                       else {
                           this.check_required(e);
                       }
                   },

                   hide_all: function(e) {
                       this.pane.hide();
                       if (this.flyoutpane) {
                           this.flyoutpane.hide();
                       }
                       this.input.trigger("fb-pane-hide", this);
                       this.input.trigger("fb-flyoutpane-hide", this);
                   },

                   request: function(val, start) {
									 	  
                               
                       var self = this,
                       o = this.options;

                       if (this.ac_xhr) {
                           this.ac_xhr.abort();
                           this.ac_xhr = null;
                       }
                       var data = {
                           prefix: val
                       };
                       if (start) {
                           data.start = start;
                       }

                       $.extend(data, o.ac_param);

                       var url = o.service_url + o.service_path + "?" + $.param(data),
                       cached = $.suggest.cache[url];
                       if (cached) {
                           this.response(cached, start ? start : -1, true);
                           return;
                       }

                       clearTimeout(this.request.timeout);

                       /* Added by Adelein */
                       data.prefix =  extractLast(data.prefix)
											 /* Added by Adelein */
											
                       var ajax_options = {
                           url: o.service_url + o.service_path,
                           data: data,
                           beforeSend: function(xhr) {
                               var calls =
                                   self.input.data("request.count.suggest") || 0;
                               if (!calls) {
                                   self.trackEvent(self.name, "start_session");
                               }
                               calls += 1;
                               self.trackEvent(self.name, "request",
                                               "count", calls);
                               self.input.data("request.count.suggest", calls);
                           },
                           success: function(data) {
                               $.suggest.cache[url] = data;
                               data.prefix = val;  // keep track of prefix to match up response with input value
                               self.response(data, start ? start : -1);
                           },
                           error: function(xhr) {
                               self.status_error();
                               self.trackEvent(self.name, "request", "error", {
                                                   url:this.url,
                                                   response: xhr ? xhr.responseText : ''});
                               self.input.trigger("fb-error", Array.prototype.slice.call(arguments));
                           },
                           complete: function(xhr) {
                               if (xhr) {
                                   self.trackEvent(self.name, "request", "tid",
                                                   xhr.getResponseHeader("X-Metaweb-TID"));
                               }
                           },
                           dataType: self.jsonp ? "jsonp" : "json",
                           cache: true
                       };

                       this.request.timeout =
                           setTimeout(function() {
                                          self.ac_xhr = $.ajax(ajax_options);
                                      }, o.xhr_delay);
                   },

                   create_item: function(data, response_data) {
                       var css = this.options.css;

                       var li =  $("<li>").addClass(css.item);

                       var name = $("<div>").addClass(css.item_name)

                           .append($("<label>")
                           .append($.suggest.strongify(data.name || data.guid,
                                                       response_data.prefix))),
                       types = data.type;
                       // this converts html escaped strings like "&amp;"
                       // back to "&"
                       data.name = name.text();
                       li.append(name);

                       var nt = data['n:type'] || data['notable:type'];
                       if (nt) {
                           if (typeof nt === 'object') {
                               // as of client/dev/108 n:type
                               // (previously notable:type) is an object
                               // and already calculated
                               name.prepend($("<div>").addClass(css.item_type)
                                            .text(nt.name));
                           }
                           else {
                               var notable, type, is_topic = false;
                               $.each(data.type, function(i,n) {
                                          if (n.id === nt) {
                                              notable = n.name;
                                          }
                                          if (n.id === '/common/topic') {
                                              is_topic = 'Topic';
                                          }
                                          else if (!type) {
                                              type = n.name;
                                          }
                                      });
                               if (notable || type || is_topic) {
                                   name.prepend($("<div>")
                                                .addClass(css.item_type)
                                                .text(notable || type
                                                      || is_topic));
                               }
                           }

                       }


                       //console.log("create_item", li);
                       return li;
                   },


                   mouseover_item_hook: function(li) {
                       var data = li.data("data.suggest");
                       if (this.options.flyout) {
                           if (data) {
                               this.flyout_request(data);
                           }
                           else {
                               //this.flyoutpane.hide();
                           }
                       }
                   },

                   check_response: function(response_data) {
                       return response_data.prefix === this.input.val();
                   },

                   response_hook: function(response_data, start) {
                       if (this.flyoutpane) {
                           this.flyoutpane.hide();
                       }
                       if (start > 0) {
                           $(".fbs-more", this.pane).remove();
                       }
                       else {
                           //this.pane.hide();
                           this.list.empty();
                       }
                   },

                   show_hook: function(response_data, start, first) {
                       base.show_hook.apply(this, [response_data]);

                       var o = this.options,
                       self = this,
                       p = this.pane,
                       l = this.list,
                       result = response_data.result;

                       var more = $(".fbs-more", p),
                       suggestnew = $(".fbs-suggestnew", p);


                       // more
                       if (result && result.length && "start" in response_data) {
                           if (!more.length) {
                               var more_link = $('<a class="fbs-more-link" href="#" title="(Ctrl+m)">view more</a>');
                               more = $('<div class="fbs-more">')
                                   .append(more_link);
                               more_link
                                   .bind("click.suggest", function(e) {
                                             e.preventDefault();
                                             e.stopPropagation();
                                             var m = $(this).parent(".fbs-more");
                                             self.more(m.data("start.suggest"));
                                         });
                               l.after(more);
                           }
                           more.data("start.suggest", response_data.start);
                           more.show();
                       }
                       else {
                           more.remove();
                       }

                       // suggest_new
                       if (o.suggest_new) {
                           if (!suggestnew.length) {
                               // create suggestnew option
                               var button = $('<button class="fbs-suggestnew-button">');
                               button.text(o.suggest_new);
                               suggestnew = $('<div class="fbs-suggestnew">')
                                   .append('<div class="fbs-suggestnew-description">Your item not in the list?</div>')
                                   .append(button)
                                   .append('<span class="fbs-suggestnew-shortcut">(Shift+Enter)</span>')
                                   .bind("click.suggest", function(e) {
                                             e.stopPropagation();
                                             self.suggest_new(e);
                                         });
                               p.append(suggestnew);
                           }
                           suggestnew.show();
                       }
                       else {
                           suggestnew.remove();
                       }

                       // scroll to first if clicked on "more"
                       if (first && first.length && start > 0) {
                           var top = first.prevAll().length * first.outerHeight();
                           var scrollTop = l.scrollTop();
                           l.animate({scrollTop: top}, "slow",
                                     function(){ first.trigger("mouseover.suggest");});
                       }
                   },

                   suggest_new: function(e) {
                       var v = this.input.val();
                       if (v === "") {
                           return;
                       }
                       //console.log("suggest_new", v);
                       this.input
                           .data("data.suggest", v)
                           .trigger("fb-select-new", v);
                       this.trackEvent(this.name, "fb-select-new", "index", "new");
                       this.hide_all();
                   },

                   more: function(start) {
                       if (start) {
                           var orig = this.input.data("original.suggest");
                           if (orig !== null) {
                               this.input.val(orig);
                           }
                           this.request(this.input.val(), start);
                           this.trackEvent(this.name, "more", "start", start);
                       }
                       return false;
                   },

                   flyout_request: function(data) {
                       var self = this;
                       if (this.flyout_xhr) {
                           this.flyout_xhr.abort();
                           this.flyout_xhr = null;
                       }

                       var o = this.options,
                       sug_data = this.flyoutpane.data("data.suggest");
                       if (sug_data && data.id === sug_data.id) {
                           if (!this.flyoutpane.is(":visible")) {
                               var s = this.get_selected();
                               this.flyout_position(s);
                               this.flyoutpane.show();
                               this.input.trigger("fb-flyoutpane-show", this);
                           }
                           return;
                       }

                       // check $.suggest.flyout.cache
                       var cached = $.suggest.flyout.cache[data.id];
                       if (cached && cached.id && cached.html) {
                           // CLI-10009: use cached item only if id and html present
                           this.flyout_response(cached);
                           return;
                       }

                       //this.flyoutpane.hide();

                       var submit_data = {
                           id: data.id
                       };
                       if (o.as_of_time) {
                           submit_data.as_of_time = o.as_of_time;
                       }

                       var ajax_options = {
                           url: o.flyout_service_url + o.flyout_service_path,
                           data: submit_data,
                           beforeSend: function(xhr) {
                               var calls = self.input.data("flyout.request.count.suggest") || 0;
                               calls += 1;
                               self.trackEvent(self.name, "flyout.request",
                                               "count", calls);
                               self.input.data("flyout.request.count.suggest",
                                               calls);
                           },
                           success: function(data) {
                               data = self.jsonp ? data : {
                                   id: submit_data.id,
                                   html: data
                               };
                               $.suggest.flyout.cache[data.id] = data;
                               self.flyout_response(data);
                           },
                           error: function(xhr) {
                               self.trackEvent(self.name, "flyout", "error", {
                                                   url:this.url,
                                                   response: xhr ? xhr.responseText : ''
                                               });
                           },
                           complete: function(xhr) {
                               if (xhr) {
                                   self.trackEvent(self.name, "flyout", "tid",
                                                   xhr.getResponseHeader("X-Metaweb-TID"));
                               }
                           },
                           dataType: self.jsonp ? "jsonp" : "html",
                           cache: true
                       };

                       //var self = this;
                       clearTimeout(this.flyout_request.timeout);
                       this.flyout_request.timeout =
                           setTimeout(function() {
                                          self.flyout_xhr = $.ajax(ajax_options);
                                      }, o.xhr_delay);

                       this.input.trigger("fb-request-flyout", ajax_options);
                   },

                   flyout_response: function(data) {
                       var o = this.options,
                       p = this.pane,
                       s = this.get_selected() || [];
                       if (p.is(":visible") && s.length) {
                           var sug_data = s.data("data.suggest");
                           if (sug_data && data.id === sug_data.id && data.html) {
                               this.flyoutpane.html(data.html);
                               this.flyout_position(s);
                               this.flyoutpane.show()
                                   .data("data.suggest", sug_data);
                               this.input.trigger("fb-flyoutpane-show", this);
                           }
                       }
                   },

                   flyout_position: function($item) {
                       if (this.options.flyout_parent) {
                           return;
                       }

                       var p = this.pane,
                       fp = this.flyoutpane,
                       css = this.options.css,
                       pos = undefined,
                       old_pos = {
                           top: parseInt(fp.css("top"), 10),
                           left: parseInt(fp.css("left"), 10)
                       },
                       pane_pos = p.offset(),
                       pane_width = p.outerWidth(),
                       flyout_height = fp.outerHeight(),
                       flyout_width = fp.outerWidth();

                       if (this.options.flyout === "bottom") {
                           // flyout position on top/bottom
                           pos = pane_pos;
                           var input_pos = this.input.offset();
                           if (pane_pos.top < input_pos.top) {
                               pos.top -= flyout_height;
                           }
                           else {
                               pos.top += p.outerHeight();
                           }
                           fp.addClass(css.flyoutpane + "-bottom");
                       }
                       else {
                           pos = $item.offset();
                           var item_height = $item.outerHeight();

                           pos.left += pane_width;
                           var flyout_right = pos.left + flyout_width,
                           scroll_left =  $(document.body).scrollLeft(),
                           window_right = $(window).width() + scroll_left;

                           pos.top = pos.top + item_height - flyout_height;
                           if (pos.top < pane_pos.top) {
                               pos.top = pane_pos.top;
                           }

                           if (flyout_right > window_right) {
                               var left = pos.left - (pane_width + flyout_width);
                               if (left > scroll_left) {
                                   pos.left = left;
                               }
                           }
                           fp.removeClass(css.flyoutpane + "-bottom");
                       }

                       if (!(pos.top === old_pos.top &&
                             pos.left === old_pos.left)) {
                           fp.css({top:pos.top, left:pos.left});
                       }
                   },

                   hoverout_list: function(e) {
                       if (this.flyoutpane && !this.get_selected()) {
                           this.flyoutpane.hide();
                       }
                   }
               });

     // Freebase suggest settings
     $.extend($.suggest.suggest, {

                  defaults: {

                      type: null,

                      type_strict: "any",

                      mql_filter: null,

                      as_of_time: null,

                      // base url for autocomplete service
                      service_url: "http://www.freebase.com",

                      // service_url + service_path = url to autocomplete service
                      service_path: "/private/suggest",

                      // 'left', 'right' or null
                      // where list will be aligned left or right with the input
                      align: null,

                      // whether or not to show flyout on mouseover
                      flyout: true,

                      // default is service_url if NULL
                      flyout_service_url: null,

                      // flyout_service_url + flyout_service_path =
                      // url to flyout service
                      flyout_service_path: "/private/flyout",

                      // jQuery selector to specify where the flyout
                      // will be appended to (defaults to document.body).
                      flyout_parent: null,

                      // text snippet you want to show for the suggest
                      // new option
                      // clicking will trigger an fb-select-new event
                      // along with the input value
                      suggest_new: null,

                      nomatch: '<em class="fbs-nomatch-text">No suggested matches.</em><h3>Tips on getting better suggestions:</h3><ul class="fbs-search-tips"><li>Enter more or fewer characters</li><li>Add words related to your original search</li><li>Try alternate spellings</li><li>Check your spelling</li></ul>',

                      // CSS default class names
                      css: {
                          item_type: "fbs-item-type",
                          flyoutpane: "fbs-flyout-pane"
                      },

                      // the delay before sending off the ajax request to the
                      // suggest and flyout service
                      xhr_delay: 200,

                      // return type information for each suggest item returned
                      all_types: false
                  }
              });


     var f = document.createElement("input");

 })(jQuery);


/**
 * http://www.JSON.org/json2.js
 **/
if (! ("JSON" in window && window.JSON)){JSON={}}(function(){function f(n){return n<10?"0"+n:n}if(typeof Date.prototype.toJSON!=="function"){Date.prototype.toJSON=function(key){return this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z"};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(key){return this.valueOf()}}var cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,gap,indent,meta={"\b":"\\b","\t":"\\t","\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"},rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?'"'+string.replace(escapable,function(a){var c=meta[a];return typeof c==="string"?c:"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+'"':'"'+string+'"'}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==="object"&&typeof value.toJSON==="function"){value=value.toJSON(key)}if(typeof rep==="function"){value=rep.call(holder,key,value)}switch(typeof value){case"string":return quote(value);case"number":return isFinite(value)?String(value):"null";case"boolean":case"null":return String(value);case"object":if(!value){return"null"}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==="[object Array]"){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||"null"}v=partial.length===0?"[]":gap?"[\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"]":"["+partial.join(",")+"]";gap=mind;return v}if(rep&&typeof rep==="object"){length=rep.length;for(i=0;i<length;i+=1){k=rep[i];if(typeof k==="string"){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}else{for(k in value){if(Object.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}v=partial.length===0?"{}":gap?"{\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"}":"{"+partial.join(",")+"}";gap=mind;return v}}if(typeof JSON.stringify!=="function"){JSON.stringify=function(value,replacer,space){var i;gap="";indent="";if(typeof space==="number"){for(i=0;i<space;i+=1){indent+=" "}}else{if(typeof space==="string"){indent=space}}rep=replacer;if(replacer&&typeof replacer!=="function"&&(typeof replacer!=="object"||typeof replacer.length!=="number")){throw new Error("JSON.stringify")}return str("",{"":value})}}if(typeof JSON.parse!=="function"){JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==="object"){for(k in value){if(Object.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v}else{delete value[k]}}}}return reviver.call(holder,key,value)}cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,""))){j=eval("("+text+")");return typeof reviver==="function"?walk({"":j},""):j}throw new SyntaxError("JSON.parse")}}}());


jQuery.suggest.version='Version:r102244:102278 Built:Wed Oct 27 2010 by daepark';