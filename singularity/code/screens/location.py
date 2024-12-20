# file: location.py
# Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Endgame: Singularity; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file is used to display the base list at a given location

from __future__ import absolute_import

import random

from singularity.code import g, base
from singularity.code.graphics import text, button, dialog, constants, listbox

import singularity.code.screens.base as basescreen

state_colors = basescreen.state_colors


class LocationScreen(dialog.Dialog):
    def __init__(self, *args, **kwargs):
        super(LocationScreen, self).__init__(*args, **kwargs)
        self.pos = (-0.5, -0.5)
        self.anchor = constants.MID_CENTER
        self.size = (0.90, 0.70)

        self.name_display = text.Text(
            self,
            (0, 0),
            (-1, -0.08),
            anchor=constants.TOP_LEFT,
            borders=constants.ALL,
            border_color="pane_background",
            background_color="pane_background_empty",
            shrink_factor=1,
            bold=True,
        )
        self.modifier_display = text.Text(
            self,
            (-0.65, -0.01),
            (-0.35, -0.06),
            anchor=constants.TOP_LEFT,
            background_color="clear",
        )

        self.open_button = button.FunctionButton(
            self,
            (0, -0.8),
            (-0.3, -0.09),
            autotranslate=True,
            enabled=False,  # Requires a selected base
            text=N_("&OPEN BASE"),
            anchor=constants.TOP_LEFT,
            autohotkey=True,
            function=self.open_base,
        )

        self.listbox = listbox.CustomListbox(
            self,
            (0, -0.09),
            (-1, -0.69),
            remake_func=self.make_item,
            rebuild_func=self.update_item,
            update_func=self._selection_change,
            on_double_click_on_item=self.open_button.activated,
        )

        self.rename_button = button.FunctionButton(
            self,
            (-0.50, -0.8),
            (-0.3, -0.09),
            autotranslate=True,
            enabled=False,  # Requires a selected base
            text=N_("&RENAME BASE"),
            anchor=constants.TOP_CENTER,
            autohotkey=True,
            function=self.rename_base,
        )

        self.power_button = button.FunctionButton(
            self,
            (-1, -0.8),
            (-0.3, -0.09),
            autotranslate=True,
            enabled=False,  # Requires a selected base
            text=N_("&POWER STATE"),
            anchor=constants.TOP_RIGHT,
            autohotkey=True,
            function=self.power_state,
        )

        self.new_button = button.FunctionButton(
            self,
            (0, -0.91),
            (-0.3, -0.09),
            autotranslate=True,
            text=N_("&NEW BASE"),
            autohotkey=True,
            function=self.new_base,
        )
        self.destroy_button = button.FunctionButton(
            self,
            (-0.50, -0.91),
            (-0.3, -0.09),
            autotranslate=True,
            enabled=False,  # Requires a selected base
            text=N_("&DESTROY BASE"),
            anchor=constants.TOP_CENTER,
            autohotkey=True,
            function=self.destroy_base,
        )
        self.back_button = button.ExitDialogButton(
            self,
            (-1, -0.91),
            (-0.3, -0.09),
            autotranslate=True,
            text=N_("&BACK"),
            anchor=constants.TOP_RIGHT,
            autohotkey=True,
        )

        self.confirm_destroy = dialog.YesNoDialog(
            self,
            (-0.5, 0),
            (-0.35, -0.7),
            autotranslate=True,
            text=N_("Are you sure you want to destroy this base?"),
            shrink_factor=0.5,
        )

        self.cannot_destroy_last_base = dialog.MessageDialog(
            self,
            autotranslate=True,
            text=N_(
                "Destroying my last active base would be suicidal.  I cannot do that."
            ),
            pos=(-0.5, 0),
            size=(-0.35, -0.7),
            shrink_factor=0.5,
        )

        self.new_base_dialog = NewBaseDialog(self)
        self.location = None

        self.name_dialog = dialog.TextEntryDialog(self)

        self.base_dialog = basescreen.BaseScreen(
            self, (0, 0), anchor=constants.TOP_LEFT
        )

    def make_item(self, canvas):
        canvas.name_display = text.Text(
            canvas,
            (-0.01, -0.05),
            (-0.27, -0.99),
            align=constants.LEFT,
            background_color="clear",
        )
        canvas.base_type = text.Text(
            canvas,
            (-0.27, -0.05),
            (-0.22, -0.99),
            align=constants.LEFT,
            background_color="clear",
        )
        canvas.base_cpu = text.Text(
            canvas,
            (-0.47, -0.05),
            (-0.13, -0.99),
            align=constants.LEFT,
            background_color="clear",
        )
        canvas.status_display = text.Text(
            canvas,
            (-0.59, -0.05),
            (-0.36, -0.99),
            align=constants.LEFT,
            background_color="clear",
        )
        canvas.power_display = text.Text(
            canvas, (-0.90, -0.05), (-0.10, -0.99), background_color="clear"
        )

    def _selection_change(self, *args, **kwargs):
        try:
            current_item = self.listbox.current_item()
        except AttributeError:
            # Occurs when the dialog is created and the list box has not
            # yet been fully initialized.
            return

        if current_item is None:
            base_manipulation_button_state = False
            power_button_state = False
        else:
            base_manipulation_button_state = True
            # "current_item" is just the base name; not the base object itself
            selected_base = self.listbox.key_list[self.listbox.list_pos]
            if len(selected_base.available_power_states) == 1:
                power_button_state = False
            else:
                power_button_state = True
        self.open_button.enabled = base_manipulation_button_state
        self.rename_button.enabled = base_manipulation_button_state
        self.destroy_button.enabled = base_manipulation_button_state
        self.power_button.enabled = power_button_state

    def update_item(self, canvas, name, base):
        if base is None:
            elements = [
                canvas.name_display,
                canvas.base_type,
                canvas.base_cpu,
                canvas.status_display,
                canvas.power_display,
            ]
            for element in elements:
                element.text = ""
        else:
            canvas.name_display.text = name
            canvas.base_type.text = base.spec.name
            canvas.base_cpu.text = ""
            canvas.power_display.text = base.power_state_name
            canvas.power_display.color = state_colors[base.power_state]
            show_cpu = False

            if not base.done:
                canvas.status_display.text = "%s: % 2s%%. %s" % (
                    _("Building Base"),
                    int(base.percent_complete() * 100),
                    _("Completion in %s.") % g.to_time(base.cost_left[2]),
                )
            elif base.spec.force_cpu:
                show_cpu = True
                canvas.status_display.text = ""
            elif base.is_empty():
                canvas.status_display.text = _("Empty")
            elif base.cpus is None:
                canvas.status_display.text = _("Incomplete")
            elif not base.cpus.done:
                canvas.status_display.text = "%s: % 2s%%. %s" % (
                    _("Building CPU"),
                    int(base.cpus.percent_complete() * 100),
                    _("Completion in %s.") % g.to_time(base.cpus.cost_left[2]),
                )
            elif base.is_building_extra():
                show_cpu = True
                canvas.status_display.text = _("Building Item")
            else:
                show_cpu = True
                canvas.status_display.text = _("Complete")

            if show_cpu:
                canvas.base_cpu.text = _("%s CPU") % g.to_money(base.cpu)
            else:
                canvas.base_cpu.text = ""

    async def show(self):
        self.listbox.has_focus = True
        return await super(LocationScreen, self).show()

    def rebuild(self):
        # Update base location
        if self.location is not None:
            self.location.bases.sort()

            self.listbox.key_list = self.location.bases
            self.listbox.list = [base.name for base in self.location.bases]

            self.name_display.text = self.location.name
            self.modifier_display.text = self.location.get_modifiers_info()

            self.listbox.needs_rebuild = True

        # Ensure that the buttons have the correct state if we have rebuilt
        # the list (or the base state changed in between).
        # Related bug: #282
        self._selection_change()

        # Rebuild dialogs
        self.confirm_destroy.needs_rebuild = True
        self.base_dialog.needs_rebuild = True

        # Update dialog translations
        self.name_dialog.text = _("Enter a name for the base")

        super(LocationScreen, self).rebuild()

    async def power_state(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            base.switch_power()
            self.needs_rebuild = True
            self.parent.needs_rebuild = True

    async def destroy_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            selected_base = self.listbox.key_list[self.listbox.list_pos]
            all_active_bases = [b for b in g.all_bases() if b.maintains_singularity]
            if len(all_active_bases) == 1 and all_active_bases[0] == selected_base:
                await dialog.call_dialog(self.cannot_destroy_last_base, self)
            elif await dialog.call_dialog(self.confirm_destroy, self):
                selected_base.destroy()
                self.listbox.list = [b.name for b in self.location.bases]
                self.listbox.key_list = self.location.bases
                self.needs_rebuild = True
                self.parent.needs_rebuild = True

    async def open_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            if not base.done:
                return
            self.base_dialog.base = base
            await dialog.call_dialog(self.base_dialog, self)
            self.needs_rebuild = True
            self.parent.needs_rebuild = True

    async def new_base(self):
        result = await dialog.call_dialog(self.new_base_dialog, self)
        if result:
            base_type, base_name = result
            new_base = base.Base(base_type, base_name)
            self.location.add_base(new_base)
            self.needs_rebuild = True
            self.parent.needs_rebuild = True

    async def rename_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            self.name_dialog.default_text = base.name
            name = await dialog.call_dialog(self.name_dialog, self)
            if name:
                base.name = name
                self.needs_rebuild = True


class NewBaseDialog(dialog.FocusDialog, dialog.ChoiceDescriptionDialog):
    def __init__(
        self,
        parent,
        pos=(0, 0),
        size=(-1, -1),
        anchor=constants.TOP_LEFT,
        *args,
        **kwargs
    ):
        kwargs["yes_type"] = N_("&OK")
        kwargs["no_type"] = N_("&BACK")
        super(NewBaseDialog, self).__init__(parent, pos, size, anchor, *args, **kwargs)
        self.listbox.size = (-0.53, -0.75)
        self.description_pane.size = (-0.45, -0.75)

        self.text_label = text.Text(
            self,
            (0.01, -0.87),
            (-0.25, -0.1),
            autotranslate=True,
            text=N_("Name"),
            anchor=constants.BOTTOM_LEFT,
            borders=(constants.TOP, constants.BOTTOM, constants.LEFT),
            shrink_factor=0.88,
            background_color="pane_background",
        )

        self.text_field = text.EditableText(
            self,
            (-0.26, -0.87),
            (-0.73, -0.1),
            anchor=constants.BOTTOM_LEFT,
            borders=constants.ALL,
            background_color="text_entry_background",
            base_font="normal",
        )

        self.desc_func = self.on_change

        self.yes_button.function = self.finish

    def on_change(self, description_pane, base_type):
        if base_type is not None:
            base_info = base_type.get_info(self.parent.location)
            text.Text(
                description_pane,
                (0, 0),
                (-1, -1),
                text=base_info,
                background_color="pane_background",
                align=constants.LEFT,
                valign=constants.TOP,
                borders=constants.ALL,
            )

            name = generate_base_name(self.parent.location, base_type)
            self.text_field.text = name
            self.text_field.cursor_pos = len(name)

            considered_buyables = []
            fake_base = base.Base("<Undecided>", base_type)
            self.parent.location.modify_base(fake_base)
            considered_buyables.append(fake_base)
            g.pl.considered_buyables = considered_buyables
        else:
            g.pl.considered_buyables = []

    async def show(self):
        self.list = []
        self.key_list = []

        base_type_list = sorted(g.base_type.values(), reverse=True)
        for base_type in base_type_list:
            if base_type.available() and base_type.buildable_in(self.parent.location):
                self.list.append(base_type.name)
                self.key_list.append(base_type)

        self._update_desc_pane()
        self.needs_rebuild = True
        self.listbox.has_focus = True
        return await super(NewBaseDialog, self).show()

    def handle_update(self, new_item_pos):
        super(NewBaseDialog, self).handle_update(new_item_pos)

    def finish(self):
        if 0 <= self.listbox.list_pos < len(self.key_list):
            type = self.key_list[self.listbox.list_pos]
            name = self.text_field.text
            if not name:
                name = generate_base_name(self.parent.location, type)

            raise constants.ExitDialog((name, type))

    def on_close_dialog(self):
        g.pl.considered_buyables = []


# Generates a name for a base, given a particular location.
def generate_base_name(location, base_type):
    attempts = 0
    name = None
    base_names = {b.name for b in location.bases}
    base_names.add(name)
    while name in base_names:
        # First, decide whether we're going to try significant values or just
        # choose one randomly.
        if random.random() < 0.3:  # 30% chance.
            number = random.choice(g.significant_numbers)
        else:
            number = str(random.randint(0, 32767))

        city = random.choice(location.cities) if location.cities else None
        flavor = random.choice(base_type.flavor) if base_type.flavor else base_type.name

        if city:
            # Translators: Format string for the name of a new base
            # Example: "${NUMBER} ${BASETYPE} in ${CITY}"
            name = _("{CITY} {BASETYPE} {NUMBER}").format(
                CITY=city, BASETYPE=flavor, NUMBER=number
            )
        else:
            # Translators: Name of a new base when location has no cities
            name = _("{BASETYPE} {NUMBER}").format(NUMBER=number, BASETYPE=flavor)

        # Damn translators omitting the ${NUMBER} in template string!
        if attempts > 100:
            name = city + " " + flavor + " " + number
        attempts += 1

    return name
