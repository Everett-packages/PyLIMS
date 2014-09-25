
function HUD_set_status_working()
{
   document.getElementById('HUD_status').innerHTML = "<img src='" + pylims.cgiVars.module_file_dir + "/img/HUD_animated_working.gif'>\n";
}

function HUD_set_status_idle()
{
   document.getElementById('HUD_status').innerHTML = "<img src='" + pylims.cgiVars.module_file_dir + "/img/HUD_status_idle.png'>\n";
}

function HUD_load_logout_button()
{
   document.getElementById('HUD_logout').innerHTML = "<a onClick='user_logout()'><img src='" +
                                                       pylims.cgiVars.module_file_dir + "/img/HUD_logout.png'></a>\n";
}

function HUD_load_log_button()
{
   document.getElementById('HUD_log').innerHTML = "<a href='" + pylims.cgiVars.cgi_log_file + "'><img src='" +
                                                   pylims.cgiVars.module_file_dir + "/img/HUD_CGI_log.png'></a>\n";
}

function HUD_load_menu_button()
{
   document.getElementById('HUD_menu').innerHTML = "<img src='" + pylims.cgiVars.module_file_dir + "/img/HUD_menu.png'>\n";
}

function HUD_load_search_button()
{
   document.getElementById('HUD_search').innerHTML = "<img src='" + pylims.cgiVars.module_file_dir + "/img/HUD_search.png'>\n";
}

function HUD_load_default_buttons()
{
   HUD_set_status_idle();
   HUD_load_logout_button();
   HUD_load_log_button();
   HUD_load_menu_button();
   HUD_load_search_button();
}

function user_logout()
{
    var c = document.cookie.split(';');
    for (var i = 0; i < c.length; i++)
    {
       var v = c[i].split("=");
       document.cookie =  v[0].trim() + '=; expires=Thu, 01-Jan-70 00:00:01 GMT; path=/';
    }
    window.location = document.URL;
}