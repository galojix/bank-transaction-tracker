//"Select/Unselect All" for category names checkboxes
$("#category_names_selectall").change(function(){
    var status = this.checked;
    $('[id^=category_names]').each(function(){
        this.checked = status;
    });
});

$('[id^=category_names]').change(function(){
    // One checkbox unchecked
    if(this.checked == false){
        $("#category_names_selectall")[0].checked = false;
    }

    // All checkboxes checked
    if ($('[id^=category_names]:checked').length == $('[id^=category_names]').length ){
        $("#category_names_selectall")[0].checked = true;
    }
});

//"Select/Unselect All" for category types checkboxes
$("#category_types_selectall").change(function(){
    var status = this.checked;
    $('[id^=category_types]').each(function(){
        this.checked = status;
    });
});

$('[id^=category_types]').change(function(){
    // One checkbox unchecked
    if(this.checked == false){
        $("#category_types_selectall")[0].checked = false;
    }

    // All checkboxes checked
    if ($('[id^=category_types]:checked').length == $('[id^=category_types]').length ){
        $("#category_types_selectall")[0].checked = true;
    }
});

// "Select/Unselect All" for account names checkboxes
$("#account_names_selectall").change(function(){
    var status = this.checked;
    $('[id^=account_names]').each(function(){
        this.checked = status;
    });
});

$('[id^=account_names]').change(function(){
    // One checkbox unchecked
    if(this.checked == false){
        $("#account_names_selectall")[0].checked = false;
    }

    // All checkboxes checked
    if ($('[id^=account_names]:checked').length == $('[id^=account_names]').length ){
        $("#account_names_selectall")[0].checked = true;
    }
});
