from pyrope.formatters import TemplateFormatter

import nbformat

class LatexGenerator:

    def __init__(self, includes_solution, number_of_hints):
        self.includes_solution = includes_solution
        self.number_of_hints = number_of_hints
        self.exercise_cells = []
        self.solution_cells = []
    
    def generate_cells_of_exercise(self, pexercise):
        self.append_raw_cells('\\PyRopeExercise{')

        if pexercise.preamble != '':
            preamble = self.remove_whitespace(pexercise.preamble)
            self.append_markdown_cells(preamble, None)
        self.append_raw_cells('}')

        self.append_raw_cells('{')
        
        template = self.remove_whitespace(pexercise.model.template)
        (template_string_constructor, solution_string_constructor) = self.format_markdown(pexercise, template)

        self.append_markdown_cells(template_string_constructor, solution_string_constructor)

        max_hints = min(self.number_of_hints, pexercise.hints.__len__())

        for hint_num in range(0, max_hints):
            self.append_raw_cells('\n\\PyRopeHint{')
            
            hint = self.remove_whitespace(pexercise.hints[hint_num])
            (hints_string_constructor, solution_hints_string_constructor) = self.format_markdown(pexercise, hint)

            self.append_markdown_cells(hints_string_constructor, solution_hints_string_constructor)
            self.append_raw_cells('}')
        
        self.append_raw_cells(f'}}{{{pexercise.max_total_score:g}}}\n')

    def get_notebook_cells(self):
        return (self.exercise_cells, self.solution_cells)
    
    def remove_whitespace(self, string_with_whitespace):
        return '\n'.join([line.strip() for line in string_with_whitespace.split('\n')])
    
    def format_markdown(self, pexercise, markdown_string):
        execise_string_constructor = ''
        solution_string_constructor = ''

        for literal_text, field_name, format_spec in TemplateFormatter.parse(markdown_string):

            if literal_text:
                execise_string_constructor += literal_text
                if self.includes_solution: solution_string_constructor += literal_text

            if field_name:
                param_value = pexercise.parameters.get(field_name)
                if format_spec:
                    if format_spec == 'latex':
                        #TODO evaluate if special format handling is necessary
                        execise_string_constructor += pexercise.parameters.get(field_name).__str__()
                        if self.includes_solution: solution_string_constructor += pexercise.parameters.get(field_name).__str__()
                    else:
                        raise ValueError(f'Unknown format specifier "{format_spec}".')
                else:
                    if param_value is None:
                        for widget in pexercise.model.widgets:
                            if widget.ifield_name.__eq__(field_name):
                                execise_string_constructor += self.toLatex(widget)
                                if self.includes_solution:
                                    if pexercise.the_solution.get(field_name) is None:
                                        solution_string = pexercise.a_solution.get(field_name).__str__()
                                    else:
                                        solution_string = pexercise.the_solution.get(field_name).__str__()
                                    solution_string_constructor += f'\\PyRopeSolution{{{solution_string}}}'
                                break
                    else: 
                        execise_string_constructor += param_value.__str__()
                        if self.includes_solution: solution_string_constructor += param_value.__str__()
        return (execise_string_constructor, solution_string_constructor)
    
    def toLatex(self, widget):
        match widget.__class__.__name__:
            case 'Checkbox':
                return r"\PyRopeCheckbox"
            case 'Dropdown':
                return r"\PyRopeDropdown{" + ";".join(widget.labels) + "}"
            case 'RadioButtons':
                return r"\PyRopeRadioButtons{" + ";".join(widget.labels) + "}"
            case 'Slider':
                return fr"\PyRopeSlider{{{widget.minimum}}}{{{widget.maximum}}}"
            case 'Text':
                return r"\PyRopeText"
            case 'TextArea':
                return fr"\PyRopeTextArea{{{widget.height}}}{{{widget.width}}}"
            case _:
                return r"\PyRopeText"
            
    def append_raw_cells(self, exercise_cell_content):
        self.exercise_cells.append(nbformat.v4.new_raw_cell(exercise_cell_content))
        if self.includes_solution: self.solution_cells.append(nbformat.v4.new_raw_cell(exercise_cell_content))
            
    def append_markdown_cells(self, exercise_cell_content, solution_cell_content):
        self.exercise_cells.append(nbformat.v4.new_markdown_cell(exercise_cell_content))
        if self.includes_solution:
            if solution_cell_content is None:
                self.solution_cells.append(nbformat.v4.new_markdown_cell(exercise_cell_content))
            else:
                self.solution_cells.append(nbformat.v4.new_markdown_cell(solution_cell_content))

