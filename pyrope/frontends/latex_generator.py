from pyrope.formatters import TemplateFormatter

import nbformat

class LaTeXGenerator:

    def __init__(self, includes_solution, number_of_hints):
        self.includes_solution = includes_solution
        self.number_of_hints = number_of_hints
        self.exercise_cells = []
        self.solution_cells = []
    
    def generate_cells_of_exercise(self, pexercise):
        self.exercise_cells.append(nbformat.v4.new_raw_cell('\\PyRopeExercise{'))
        if self.includes_solution: self.solution_cells.append(nbformat.v4.new_raw_cell('\\PyRopeExercise{'))

        if pexercise.preamble != '':
            preamble = '\n'.join([line.strip() for line in pexercise.preamble.split('\n')])
            self.exercise_cells.append(nbformat.v4.new_markdown_cell(preamble))
            if self.includes_solution: self.solution_cells.append(nbformat.v4.new_markdown_cell(preamble))
        self.exercise_cells.append(nbformat.v4.new_raw_cell('}'))
        if self.includes_solution: self.solution_cells.append(nbformat.v4.new_raw_cell('}'))

        self.exercise_cells.append(nbformat.v4.new_raw_cell('{'))
        if self.includes_solution: self.solution_cells.append(nbformat.v4.new_raw_cell('{'))
        template = '\n'.join([line.strip() for line in pexercise.model.template.split('\n')])
        
        (template_string_constructor, solution_string_constructor) = self.format_markdown(pexercise, template)

        self.exercise_cells.append(nbformat.v4.new_markdown_cell(template_string_constructor))
        if self.includes_solution: self.solution_cells.append(nbformat.v4.new_markdown_cell(solution_string_constructor))

        max_hints = min(self.number_of_hints, pexercise.hints.__len__())

        for hint_num in range(0, max_hints):
            self.exercise_cells.append(nbformat.v4.new_raw_cell('\n\\PyRopeHint{'))
            if self.includes_solution: self.solution_cells.append(nbformat.v4.new_raw_cell('\n\\PyRopeHint{'))
            
            (hints_string_constructor, solution_hints_string_constructor) = self.format_markdown(pexercise, pexercise.hints[hint_num])

            self.exercise_cells.append(nbformat.v4.new_markdown_cell(hints_string_constructor))
            if self.includes_solution: self.solution_cells.append(nbformat.v4.new_markdown_cell(solution_hints_string_constructor))

            self.exercise_cells.append(nbformat.v4.new_raw_cell('}'))
            if self.includes_solution: self.solution_cells.append(nbformat.v4.new_raw_cell('}'))
        
        self.exercise_cells.append(nbformat.v4.new_raw_cell(f'}}{{{pexercise.max_total_score:g}}}\n'))
        if self.includes_solution: self.solution_cells.append(nbformat.v4.new_raw_cell(f'}}{{{pexercise.max_total_score:g}}}\n'))

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
                if format_spec:
                    #TODO special format handling
                    execise_string_constructor += pexercise.parameters.get(field_name).__str__()
                    if self.includes_solution: solution_string_constructor += pexercise.parameters.get(field_name).__str__()
                else:
                    param_value = pexercise.parameters.get(field_name)
                    if param_value is None:
                        for widget in pexercise.model.widgets:
                            if widget.ifield_name.__eq__(field_name):
                                execise_string_constructor += widget.toLaTeX()
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
