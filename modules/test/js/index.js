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