# BurpPlugins
It's a repo for BurpSuite plugins.

# List of plugins:
1. Headers JAR
2. REST API Target
3. Cookie Jar Cleaner 

# Headers JAR
Plugin for updating headers automatically, e.g. to update Bearer after the expiration of the old one.
It contains two SessionHandlingAction:
- UpdateHeaders *(update headers from JAR)*
- AddHeaders *(add new headers to JAR)*

Also plugin provides Tab with confuguration and logs panels.

## Usage
* Create Session Handling Rules in tab *Project Options/Sessions*:
  - One rule for catching new headers and adding them into Headers JAR(e.g. catch new Header from Proxy-Browser).
    ![alt text](https://github.com/MD-Levitan/BurpPlugins/edit/master/.README/Headers/add_details.png "Details of 1-st rule")
    ![alt text](https://github.com/MD-Levitan/BurpPlugins/edit/master/.README/Headers/add_rule.png "Rule Action of 1-st rule")
    ![alt text](https://github.com/MD-Levitan/BurpPlugins/edit/master/.README/Headers/add_scope.png "Scope of 1-st rule")
  - Second rule for updating headers, you can configure rule to update all headers or update only when the header has expired.
    ![alt text](https://github.com/MD-Levitan/BurpPlugins/edit/master/.README/Headers/update_details.png "Details of 2-st rule")
    ![alt text](https://github.com/MD-Levitan/BurpPlugins/edit/master/.README/Headers/update_rule.png "Rule Action of 2-st rule")
    ![alt text](https://github.com/MD-Levitan/BurpPlugins/edit/master/.README/Headers/update_scope.png "Scope of 2-st rule")
* Open Tab *Headers JAR* and add name the header.

    


