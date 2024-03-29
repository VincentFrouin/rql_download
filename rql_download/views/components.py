#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

from cubicweb.predicates import nonempty_rset, anonymous_user
from cubicweb.web import component
from cubicweb.predicates import (
    is_instance, nonempty_rset, anonymous_user, non_final_entity)
from cubicweb.web.views.facets import (
    facets, FilterBox, FacetFilterMixIn, contextview_selector)
from logilab.mtconverter import xml_escape
from cubicweb.web.views.bookmark import BookmarksBox

# Define global search variables
RQL_DOWNLOAD_SEARCH_ENTITIES = ["Scan", "ProcessingRun", "Subject"]


###############################################################################
# Save CW search box
###############################################################################

class SaveCWSearchFilterBox(FacetFilterMixIn, component.CtxComponent):
    """ Class that enables us to display a 'Save search' box when the selected
    entities fulfill the '__select__' requirements.

    The global parameter 'RQL_DOWNLOAD_SEARCH_ENTITIES' specify with entities
    can be downloaded.
    The filter items are found dynamically.
    """
    __regid__ = "facet.filterbox"
    __select__ = ((non_final_entity() & nonempty_rset())
                  | contextview_selector())
    context = "left"
    order = 0
    title = _("Filter")

    linkbox_template = u'<div class="cw_search_box">{0}</div>'

    def render_body(self, w, **kwargs):
        """ Method that generates the html elements to display the 'Save search'
        box.

        ..note::
            This method only consider the first registered 'ns-save-search'
            action to generate the new CWSearch form.
        """

        # Get the component context
        rset, vid, divid, paginate = self._get_context()

        # Check if some facets are defined for this view
        nb_facet_widgets = len(facets(self._cw, rset, self.__regid__)[1])

        # Check if the view information can be downloaded
        can_save_search = False
        try:
            entity_name = rset.entities().next().__class__.__name__
            if entity_name in RQL_DOWNLOAD_SEARCH_ENTITIES:
               can_save_search = True
        except:
            pass
        # Can't download if not logged
        can_save_search = (can_save_search and 
                           not self._cw.session.anonymous_session)

        # Check we have a none empty rset and a valid vid
        if vid is None:
            vid = self._cw.form.get("vid")

        # Create the form url
        if can_save_search:
            w(self.search_link(rset))
        if nb_facet_widgets > 0:
            self.generate_form(w, rset, divid, vid, paginate=paginate,
                               hiddens={}, **self.cw_extra_kwargs)

    def search_link(self, rset):
        """ Method that generates a the url of the CWSearch form we want to save.
        """
        # Construct the form path
        # > get rql as url parameter
        path = u'rql={0}'.format(self._cw.url_quote(rset.printable_rql()))

        # > get the vid of the view
        if self._cw.form.get("vid"):
            path += u'&vid={0}'.format(self._cw.url_quote(self._cw.form["vid"]))

        # > say its a view
        path = u'view?' + path

        # Define the form default tile
        title = self._cw._("--unique title--")

        # Create the url to the CWSearch form
        cls = self._cw.vreg["etypes"].etype_class("CWSearch")
        add_url = cls.cw_create_url(self._cw, path=path, title=title)
        base_url = cls.cw_create_url(self._cw, title=title)
        link = (u'<a class="btn btn-primary" cubicweb:target="{0}" '
                 'id="facetBkLink" href="{1}">'.format(xml_escape(base_url),
                                                       xml_escape(add_url)))

        # Create the button
        button = u'<div class="btn-toolbar">'
        button += u'<div class="btn-group-vertical btn-block">'
        button += link
        button += u'<span class="glyphicon glyphicon-save"> {0}</span>'.format(
            self._cw._("Save search"))
        button += u'</a></div></div><br />'

        return self.linkbox_template.format(button)

    def _get_context(self):
        """ Method to get the in context box information.
        """
        view = self.cw_extra_kwargs.get("view")
        context = getattr(view, "filter_box_context_info", lambda: None)()
        if context:
            rset, vid, divid, paginate = context
        else:
            rset = self.cw_rset
            vid, divid = None, "pageContent"
            paginate = view and view.paginable
        return rset, vid, divid, paginate


###############################################################################
# Registration callback
###############################################################################

def registration_callback(vreg):
    vreg.unregister(FilterBox)
    vreg.unregister(BookmarksBox)
    vreg.register(SaveCWSearchFilterBox)

