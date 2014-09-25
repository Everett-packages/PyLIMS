
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
   document.getElementById('HUD_logout').innerHTML = "<img src='" + pylims.cgiVars.module_file_dir + "/img/HUD_logout.png'>\n";
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