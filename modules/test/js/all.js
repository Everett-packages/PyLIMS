function PyLIMS_logout()
{
    var c = document.cookie.split(';');
    for (var i = 0; i < c.length; i++)
    {
       var v = c[i].split("=");
       document.cookie =  v[0].trim() + '=; expires=Thu, 01-Jan-70 00:00:01 GMT; path=/';
    }
    document.location='../home/';
}