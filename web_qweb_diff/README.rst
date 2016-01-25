Web Qweb Diff
=============

Provides a different way to save changes in Qweb views
------------------------------------------------------

...

Features
--------

For the main feature of this module we need to consider two important moments:

1. Save an updated view.
2. Render a view taking into account the changes saved.

These moments mainly involves the models ir.ui.view and ir.qweb, then we list the issues according to this.

**Model View (ir.ui.view)**

- *Store only the difference between the original view and the updated view*. Use library diff_match_patch. The view model should have a one to many relation with a new model (ir.ui.view.diff) where the difference will be saved. In current Odoo solution the view model has a method save which is called from the interface to store each of the sections of the view, this method allows us to get each part of the view updated.

- *Track the changes of the view*. With a datetime field in the diff model we can check the order of the changes in a view, then we can reset to the last change or reset all changes to get the original view. Maybe we can consider to export changes to a file and later restore them in other database.

- *Store version without publish* Save changes as versions of a page and publish in other moment, when the user got the design desired.

**Model Qweb (ir.qweb)**

- *Render the requested view dynamically*. Look for all the diff saved for an specific view and apply to the requested view in the moment of render. This behavior should take into account the inherited views, the database could have more than one record for the same key view.

- *Save in cache the views rendered*. Maybe use cache to avoid processing of rendering views and applying patches a lot of times without new updates.

