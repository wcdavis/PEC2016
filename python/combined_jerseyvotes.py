#!/usr/bin/env python

# Combine EV_jerseyvotes.html and Senate_jerseyvotes.html

with open("EV_jerseyvotes.html", "r") as ev_file:
    ev_html = ev_file.read()

with open("Senate_jerseyvotes.html", "r") as senate_file:
    senate_html = senate_file.read()

with open("combined_jerseyvotes.html", "w") as outfile:
    outfile.write('<div id="senate_jv"><strong>Senate races</strong><br>(<a onclick="document.getElementById(\'senate_jv\').style.display=\'none\';document.getElementById(\'ev_jv\').style.display=\'\';">Presidential race</a>)%s</div>\n' % senate_html)
    outfile.write('<div id="ev_jv" style="display:none"><strong>Presidential race</strong><br>(<a onclick="document.getElementById(\'ev_jv\').style.display=\'none\';document.getElementById(\'senate_jv\').style.display=\'\';">Senate races</a>)<br>%s</div>\n' % ev_html)
