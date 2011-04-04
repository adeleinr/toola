var Helper = {};

Helper.split = function(val) {
    return val.split(/,\s*/);
}

Helper.extractLast = function(term){
  return Helper.split(term).pop();
}