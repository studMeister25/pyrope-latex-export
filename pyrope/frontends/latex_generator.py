from pyrope.formatters import TemplateFormatter
import sympy
import re

import nbformat

class LatexGenerator:

    def __init__(self, includes_solution, number_of_hints, notebook_file):
        self.includes_solution = includes_solution
        self.number_of_hints = number_of_hints
        self.notebook_file = notebook_file
        self.exercise_cells = []
        self.solution_cells = []
    
    def generate_cells_of_exercise(self, pexercise):
        self.append_raw_cells('\\PyRopeExercise{')

        if pexercise.preamble != '':
            preamble = '\n'.join([line.strip() for line in pexercise.preamble.split('\n')])
            self.append_markdown_cells(preamble, None)
        self.append_raw_cells('}')

        self.append_raw_cells('{')
        template = '\n'.join([line.strip() for line in pexercise.model.template.split('\n')])
        
        (template_string_constructor, solution_string_constructor) = self.format_markdown(pexercise, template)

        self.append_markdown_cells(template_string_constructor, solution_string_constructor)

        max_hints = min(self.number_of_hints, pexercise.hints.__len__())

        for hint_num in range(0, max_hints):
            self.append_raw_cells('\n\\PyRopeHint{')
            
            (hints_string_constructor, solution_hints_string_constructor) = self.format_markdown(pexercise, pexercise.hints[hint_num])

            self.append_markdown_cells(hints_string_constructor, solution_hints_string_constructor)
            self.append_raw_cells('}')
        
        self.append_raw_cells(f'}}{{{pexercise.max_total_score:g}}}\n')

    def get_notebook_cells(self):
        return (self.exercise_cells, self.solution_cells)
    
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
                        #try:
                        print('Latex found:')
                        print(param_value.__str__())
                            # print(re.search(fr'{field_name} =*\n',pexercise.source))
                            # sympy.init_printing()
                            # print(sympy.latex(f'sympy.{param_value.__str__()}'))
                            # execise_string_constructor += sympy.latex(f'sympy.{param_value.__str__()}')
                            # if self.includes_solution: solution_string_constructor += sympy.latex(param_value.__str__())
                        # except NameError as e:
                        #     print(e.__traceback__)
                        #     execise_string_constructor += param_value.__str__()
                        #     if self.includes_solution: solution_string_constructor += param_value.__str__()
                            
                        # print('Latex found:')
                        # nb = nbformat.v4.new_notebook()
                        # print(param_value.__str__())
                        # nb['cells'] = [nbformat.v4.new_code_cell(param_value.__str__())]

                        # nb = nbformat.validator.normalize(nb)[1]
                        # with open(self.notebook_file, 'w') as f:
                        #     nbformat.write(nb, f)

                        #TODO special format handling
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
                return "\\PyRopeCheckbox"
            case 'Dropdown':
                return "\\PyRopeDropdown{" + ";".join(widget.labels) + "}"
            case 'RadioButtons':
                return "\\PyRopeRadioButtons{" + ";".join(widget.labels) + "}"
            case 'Slider':
                return f"\\PyRopeSlider{{{widget.minimum}}}{{{widget.maximum}}}"
            case 'Text':
                return "\\PyRopeText"
            case 'TextArea':
                return f"\\PyRopeTextArea{{{widget.height}}}{{{widget.width}}}"
            case _:
                return "\\PyRopeText"
            
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

