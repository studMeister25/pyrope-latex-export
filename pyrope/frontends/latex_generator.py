
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import nbformat

from pyrope.formatters import TemplateFormatter
from pyrope.messages import (
    ChangeWidgetAttribute, CreateWidget, ExerciseAttribute, RenderTemplate,
    Submit, WaitingForSubmission, WidgetValidationError
)


@dataclass
class LaTexWidget:

    ID: UUID
    index: int
    info: str = ''
    valid: bool = None
    value: Any = None


class LaTeXGenerator:

    def __init__(self):
        self.file = None
        self.cells = []
        self.answers = {}
        self.debug = False
        self.parameters = {}
        self.runner = None
        self.total_score, self.max_total_score = None, None
        self.widgets = {}

    def set_runner(self, runner):
        self.runner = runner
        runner.register_observer(self.observer)
    
    def set_file(self, file):
        self.file = file

    def formatter(self, template, **kwargs):
        return TemplateFormatter.format(
            template, **(self.parameters | kwargs)
        )

    def render_preamble(self, preamble):
        # print('Render preamble')
        self.cells.append(nbformat.v4.new_raw_cell('\\exercise{'))
        if preamble != '':
            md_preamble = (
                f'{self.formatter(preamble)}'
            )
            # print(md_preamble)
            self.cells.append(nbformat.v4.new_markdown_cell(md_preamble))

        self.cells.append(nbformat.v4.new_raw_cell('}'))

    def render_problem(self, template):
        # print('Render problem')
        self.cells.append(nbformat.v4.new_raw_cell('{'))
        fields = {
            f'#{widget_id}': f'\\inputline'
            for widget_id, widget in self.widgets.items()
        }
        md_problem = (
            f'{self.formatter(template, **fields)}'
        )
        # print(md_problem)
        self.cells.append(nbformat.v4.new_markdown_cell(md_problem))
        self.cells.append(nbformat.v4.new_raw_cell('}'))

    def render_feedback(self, feedback):
        print('Render feedback ignored')

    def observer(self, msg):
        if self.debug:
            print(msg)

        if isinstance(msg, RenderTemplate):
            match msg.template_type:
                case 'preamble':
                    self.render_preamble(msg.template)
                case 'problem':
                    self.render_problem(msg.template)
                case 'feedback':
                    self.render_feedback(msg.template)
        elif isinstance(msg, CreateWidget):
            self.widgets[msg.widget_id] = LaTexWidget(
                msg.widget_id, len(self.widgets)
            )
        elif isinstance(msg, ExerciseAttribute):
            match msg.attribute_name:
                case 'parameters':
                    self.parameters = msg.attribute_value
                case 'answers':
                    self.answers = msg.attribute_value
                case 'total_score':
                    self.total_score = msg.attribute_value
                case 'max_total_score':
                    self.max_total_score = msg.attribute_value
                case 'debug':
                    self.debug = msg.attribute_value
                    if self.debug:
                        print(msg)
        elif isinstance(msg, ChangeWidgetAttribute):
            match msg.attribute_name:
                case 'value':
                    self.widgets[msg.widget_id].value = msg.attribute_value
                case 'valid':
                    self.widgets[msg.widget_id].valid = msg.attribute_value
                case 'info':
                    self.widgets[msg.widget_id].info = msg.attribute_value
        elif isinstance(msg, WaitingForSubmission):
            self.writeNotebook()
        elif isinstance(msg, WidgetValidationError) and not self.debug:
            print(msg)

    def notify(self, msg):
        self.runner.observer(msg)

    def writeNotebook(self):
        try:
            nb = nbformat.read(self.file, nbformat.NO_CONVERT)
            nb['cells'] = nb['cells'] + self.cells
        except FileNotFoundError:
            nb = nbformat.v4.new_notebook()
            nb['cells'] = self.cells
        nb = nbformat.validator.normalize(nb)[1]
        with open(self.file, 'w') as f:
            nbformat.write(nb, f)
