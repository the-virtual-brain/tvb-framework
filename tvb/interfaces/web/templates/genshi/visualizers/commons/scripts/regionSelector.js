/**
 * TheVirtualBrain-Framework Package. This package holds all Data Management, and
 * Web-UI helpful to run brain-simulations. To use it, you also need do download
 * TheVirtualBrain-Scientific Package (for simulators). See content of the
 * documentation-folder for more details. See also http://www.thevirtualbrain.org
 *
 * (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License version 2 as published by the Free
 * Software Foundation. This program is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
 * License for more details. You should have received a copy of the GNU General
 * Public License along with this program; if not, you can download it here
 * http://www.gnu.org/licenses/old-licenses/gpl-2.
 *
 *   CITATION:
 * When using The Virtual Brain for scientific publications, please cite it as follows:
 *
 *   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
 *   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
 *       The Virtual Brain: a simulator of primate brain network dynamics.
 *   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
 *
 * .. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
 **/

var TVBUI = TVBUI || {};

/**
 * depends on jquery and displayMessage
 * exports the RegionSelectComponent constructor
 * @module
 */
(function($, displayMessagessss){
"use strict";
/**
 * @constructor
 */
function RegionSelectComponent(dom, settings){
    var $dom = $(dom);
    var self = this;
    settings = $.extend({}, self.defaults, settings);
    self.$dom = $dom;
    self.settings = settings;
    self.selectedValues = [];
    self.namedSelections = [];
    self.allValues = [];
    self.labels = [];
    // save dom variables, set up listeners
    self.boxes = $dom.find(settings.boxesSelector);
    self.textBox = $dom.find(settings.textboxSelector);
    self.dropDown = $dom.find('select');
    self.dropDownOptions = self.dropDown.find('option');

    self.boxes.change(function(){self._onchange(this);});
    self.dropDown.change(function(){
        self.val(JSON.parse(this.value));
    });
    $dom.find(settings.checkSelector).click(function(){ self.checkAll();} );
    $dom.find(settings.uncheckSelector).click(function(){ self.clearAll();} );
    $dom.find(settings.saveSelectionButtonSelector).click(function(){ self._onNewSelection(); });

    $dom.find(settings.applySelector).click(function(){
        self.$dom.trigger("selectionApplied", [self.selectedValues.slice()]);
    });
    this.dom2model();
}

RegionSelectComponent.prototype.defaults = {
    applySelector: '.action-view',
    checkSelector: '.action-all-on',
    uncheckSelector: '.action-all-off',
    boxesSelector: 'input[type=checkbox]',
    textboxSelector : 'input[type=text]',
    saveSelectionButtonSelector : '.action-store'
};

RegionSelectComponent.prototype.change = function(fn){
    this.$dom.on("selectionChange", function(_event, arg){ fn(arg); });
};

//RegionSelectComponent.prototype.destroy = function(fn){
//    // unbind all event handlers
//    this.$dom.off(".regionselect").off(click)
//};

RegionSelectComponent.prototype.dom2model = function(){
    var self = this;
    self.allValues = [];
    self.selectedValues = [];
    self.namedSelections = [];

    this.boxes.each(function(_, el){
        self.allValues.push(el.value);
        // assumes the parent element is the label
        self.labels.push($(this).parent().text().trim());
        if(el.checked){
            self.selectedValues.push(el.value);
        }
    });
    this.dropDownOptions.each(function(i, el){
        if(i != 0){
            var $el = $(el);
            self.namedSelections.push([$el.text(), $el.val()]);
        }
    });
};

RegionSelectComponent.prototype.selectedValues2dom = function(){
    var self = this;
    this.boxes.each(function(_, el){
        var idx = self.selectedValues.indexOf(el.value);
        el.checked = idx != -1;
    });
    self.dropDownOptions = self.dropDown.find('option');
};

RegionSelectComponent.prototype._onNewSelection = function(){
    var self = this;
    var name = $.trim(self.textBox.val());
    if (name != ""){
        // add to model
        self.namedSelections.push([name, self.selectedValues.slice()]);
        // add to dom
//        var jsonval = JSON.stringify(self.selectedValues);
//        $('<option/>').val(jsonval).text(name).appendTo(self.dropDown);
//        self.dropDown.val(jsonval);
        self.textBox.val('');
        self.$dom.trigger("newSelection", [name, self.selectedValues.slice(), self.labels]);
    }else{
		displayMessage("Selection name must not be empty.", "errorMessage");
	}
};

RegionSelectComponent.prototype._onchange = function(el){
    this.dom2model();
    this.dropDown.val("[]");
    this.$dom.trigger("selectionChange", [this.selectedValues.slice()]);
};

RegionSelectComponent.prototype.val = function(arg){
    if(arg == null){
        return this.selectedValues.slice();
    }else{
        this.selectedValues = [];
        for(var i=0; i < arg.length; i++){
            // convert vals to string (as in dom)
            var val = arg[i].toString();
            // filter bad values
            if(this.allValues.indexOf(val) != -1){
                this.selectedValues.push(val);
            }else{
                console.warn("bad selection" + val);
            }
        }
        this.selectedValues2dom();
        this.$dom.trigger("selectionChange", [this.selectedValues.slice()]);
    }
};

RegionSelectComponent.prototype.clearAll = function(){
    this.dropDown.val("[]");
    this.val([]);
};

RegionSelectComponent.prototype.checkAll = function(){
    this.dropDown.val("[]");
    this.val(this.allValues);
};

// exports
TVBUI.RegionSelectComponent = RegionSelectComponent;

})($, displayMessage);  //depends


/**
 * Creates a selection component which saves selections on the server
 */
TVBUI.regionSelector = function(dom, settings){
    var connectivityGid = settings.connectivityGid;
    var component =  new TVBUI.RegionSelectComponent(dom, settings);

    function getSelections() {
        doAjaxCall({type: "POST",
            async: false,
            url: '/flow/get_available_selections',
            data: {'con_selection': component.selectedValues + '',
                   'con_labels': component.labels + '',
                   'connectivity_gid': connectivityGid},
            success: function(r) {
                component.dropDown.empty().append(r);
                component.dropDown.val('[' + component.selectedValues.join(', ')     + ']');
            } ,
            error: function(r) {
                displayMessage("Error while retrieving available selections.", "errorMessage");
            }
        });
    }

    getSelections();

    component.$dom.on("newSelection", function(_ev, name, selection, labels){
        doAjaxCall({  	type: "POST",
            url: '/flow/store_connectivity_selection/' + name,
            data: {"selection": selection + '',
                   "labels": labels + '',
                   "select_names": ''},
            success: function(r) {
                var response = $.parseJSON(r);
                if (response[0]) {
                    getSelections();
                    displayMessage(response[1], "infoMessage");
                } else {
                    displayMessage(response[1], "errorMessage");
                }
            },
            error: function() {
                displayMessage("Selection was not saved properly.", "errorMessage");
            }
        });
    });
    return component;
};


