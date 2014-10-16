function update_select_box(select_box_id, value)
{
    var box = document.getElementById(select_box_id);

    for (var i=0; i<box.length; i++)
    {
        if ( box[i].value == value )
        {
             box[i].selected = true;
        }
        else
        {
            box[i].selected = false;
        }
    }
}

function database_change(select_box_id, database_id_span)
{
    var box = document.getElementById(select_box_id);
    var v = box.options[box.selectedIndex].value;

    if ( v == 'designed sequence' )
    {
        document.getElementById(database_id_span).style.visibility='hidden';
    }
    else
    {
        document.getElementById(database_id_span).style.visibility='visible';
    }

}