
import os
import subprocess
import sys
import unittest
from uuid import uuid4
from datetime import datetime
import shutil

import nbformat

from pyrope import examples, ExercisePool, ExerciseRunner
from pyrope.core import CLIParser, ParametrizedExercise
from pyrope.formatters import TemplateFormatter
from pyrope.frontends import ConsoleFrontend, LaTeXGenerator


parser = CLIParser(prog='python3 -m pyrope')
args = parser.parse_args()

pool = ExercisePool()
if not args.filepaths:
    pool.add_exercises_from_module(examples)
else:
    for path in args.filepaths:
        pool.add_exercises_from_file(path)

if args.subcommand == 'run':

    if args.frontend == 'console':
        for exercise in pool:
            runner = ExerciseRunner(exercise, debug=args.debug)
            frontend = ConsoleFrontend()
            runner.set_frontend(frontend)
            frontend.set_runner(runner)
            runner.run()
            pexercise = runner.pexercise
            print('trivial input:', pexercise.trivial_input)
            print('dummy input:', pexercise.dummy_input)
            print('the solution:', pexercise.the_solution)
            print('a solution:', pexercise.a_solution)
            print('solution:', pexercise.solution)
            print('answers:', pexercise.answers)
            print('scores:', {
                ifield: '{}/{}'.format(
                    pexercise.scores[ifield], pexercise.max_scores[ifield]
                )
                for ifield in pexercise.ifields
            })
            print(
                f'total score: '
                f'{pexercise.total_score}/{pexercise.max_total_score}'
            )
            print('score weights:', pexercise.score_weights)
            print('correct:', pexercise.correct)

    if args.frontend == 'jupyter':
        nb = nbformat.v4.new_notebook()
        filename = str(uuid4())
        file = f'{filename}.ipynb'
        try:
            assert os.path.isdir(args.path)
        except AssertionError:
            raise NotADirectoryError(
                f'{args.path} does not exist or is not a directory.'
            )
        else:
            file = os.path.join(args.path, file)
        code = (
            'import pyrope\n\n'
            f'%pyrope run {" ".join(args.filepaths)}'
            f'{" --debug" if args.debug else ""}'
        )
        nb['exercise_cells'] = [nbformat.v4.new_code_cell(code)]
        nb.metadata['pyrope'] = {'autoexecute': True}
        nb = nbformat.validator.normalize(nb)[1]
        with open(file, 'w') as f:
            nbformat.write(nb, f)

        jupyter_server = subprocess.Popen(['jupyter', 'notebook', file])
        try:
            jupyter_server.wait()
        except KeyboardInterrupt:
            pass

        # Cleanup
        while True:
            try:
                try:
                    os.remove(file)
                except FileNotFoundError:
                    pass
                checkpoint_path = os.path.join(
                    args.path,
                    '.ipynb_checkpoints'
                )
                try:
                    checkpoint_file = os.path.join(
                        checkpoint_path,
                        f'{filename}-checkpoint.ipynb'
                    )
                    os.remove(checkpoint_file)
                except FileNotFoundError:
                    pass
                if (
                    os.path.isdir(checkpoint_path) and
                    not os.listdir(checkpoint_path)
                ):
                    os.rmdir(checkpoint_path)
                break
            except KeyboardInterrupt:
                print('Please wait for cleanup.')

if args.subcommand == 'test':
    test_cases = [
        test_case
        for exercise in pool
        for test_case in exercise.test_cases()
    ]
    suite = unittest.TestSuite(test_cases)
    runner = unittest.TextTestRunner()
    test_result = runner.run(suite)
    if not test_result.wasSuccessful():
        sys.exit(1)

if args.subcommand == 'generate':
    print('Generating LaTeX')

    # Create test folder
    test_name = args.testname
    try:
        os.mkdir(test_name)
        print(f"Directory '{test_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{test_name}' already exists; aborting...")
        sys.exit(1)


    file = 'generator.ipynb'
    try:
        assert os.path.isdir(args.path)
    except AssertionError:
        raise NotADirectoryError(
            f'{args.path} does not exist or is not a directory.'
        )
    else:
        file = os.path.join(args.path, file)
    # code = (
    #     'import pyrope\n\n'
    #     f'%pyrope run {" ".join(args.filepaths)}'
    # )
    # nb['exercise_cells'] = [nbformat.v4.new_code_cell(code)]
    # nb.metadata['pyrope'] = {'autoexecute': True}
    # nb = nbformat.validator.normalize(nb)[1]
    # with open(file, 'w') as f:
    #     nbformat.write(nb, f)

    ## pexercise.model.ifields
    ## pexercise.parameters

    amount = args.amount
    for test_num in range(1, amount+1):

        print(f'File {test_num} of {amount}')

        exercise_cells = []
        solution_cells = []

        for exercise in pool:
            exercise_cells.append(nbformat.v4.new_raw_cell('\\PyRopeExercise{'))
            solution_cells.append(nbformat.v4.new_raw_cell('\\PyRopeExercise{'))
            pexercise = ParametrizedExercise(exercise)
            if pexercise.preamble != '':
                preamble = '\n'.join([line.strip() for line in pexercise.preamble.split('\n')])
                exercise_cells.append(nbformat.v4.new_markdown_cell(preamble))
                solution_cells.append(nbformat.v4.new_markdown_cell(preamble))
            exercise_cells.append(nbformat.v4.new_raw_cell('}'))
            solution_cells.append(nbformat.v4.new_raw_cell('}'))

            exercise_cells.append(nbformat.v4.new_raw_cell('{'))
            solution_cells.append(nbformat.v4.new_raw_cell('{'))
            template = '\n'.join([line.strip() for line in pexercise.model.template.split('\n')])
            template_string_constructor = ''
            solution_string_constructor = ''

            for literal_text, field_name, format_spec in TemplateFormatter.parse(template):

                if literal_text:
                    template_string_constructor += literal_text
                    solution_string_constructor += literal_text
                    #exercise_cells.append(nbformat.v4.new_markdown_cell(literal_text))

                if field_name:
                    if format_spec:
                        #TODO special format handling
                        #exercise_cells.append(nbformat.v4.new_raw_cell(f'{pexercise.parameters.get(field_name)}'))
                        template_string_constructor += pexercise.parameters.get(field_name).__str__()
                        solution_string_constructor += pexercise.parameters.get(field_name).__str__()
                    else:
                        param_value = pexercise.parameters.get(field_name)
                        if param_value is None:
                            for widget in pexercise.model.widgets:
                                if widget.ifield_name.__eq__(field_name):
                                    #exercise_cells.append(nbformat.v4.new_raw_cell(f'{widget.toLaTeX()}'))
                                    template_string_constructor += widget.toLaTeX()
                                    if pexercise.the_solution.get(field_name) is None:
                                        solution_string = pexercise.a_solution.get(field_name).__str__()
                                    else:
                                        solution_string = pexercise.the_solution.get(field_name).__str__()
                                    solution_string_constructor += f'\\textbf{{\\underline{{ {solution_string} }}}}'
                                    break
                        else: 
                            #exercise_cells.append(nbformat.v4.new_raw_cell(f'{param_value}'))
                            template_string_constructor += param_value.__str__()
                            solution_string_constructor += param_value.__str__()

            exercise_cells.append(nbformat.v4.new_markdown_cell(template_string_constructor))
            solution_cells.append(nbformat.v4.new_markdown_cell(solution_string_constructor))
            exercise_cells.append(nbformat.v4.new_raw_cell('}\n'))
            solution_cells.append(nbformat.v4.new_raw_cell('}\n'))

        generate_solutions = args.solutions  
        if args.solutions:
            cycles = 2
        else:
            cycles = 1
        
        for cycle_num in range(0,cycles):
            nb = nbformat.v4.new_notebook()
            if cycle_num == 1:
                print('Collecting solutions')
                nb['cells'] = solution_cells
            else:
                nb['cells'] = exercise_cells
            nb = nbformat.validator.normalize(nb)[1]
            with open(file, 'w') as f:
                nbformat.write(nb, f)

            # widgets = pexercise.model.widgets
            # parameters = pexercise.parameters
            # for widget in widgets:
            #     #print(widget.ifield_name)
            #     print(widget.toLaTeX())

            os.system(f'jupyter nbconvert --to latex {file} >/dev/null 2>/dev/null')

            print('Inserting into template')

            texFile = 'generator.tex'
            try:
                assert os.path.isdir(args.path)
            except AssertionError:
                raise NotADirectoryError(
                    f'{args.path} does not exist or is not a directory.'
                )
            else:
                texFile = os.path.join(args.path, texFile)

            templateFile = 'latexTemplate.tex'
            try:
                assert os.path.isdir(args.path)
            except AssertionError:
                raise NotADirectoryError(
                    f'{args.path} does not exist or is not a directory.'
                )
            else:
                templateFile = os.path.join(args.path, templateFile)

            if cycle_num == 1:
                test_file = f'{test_name}/{test_name}-SOLUTION-{test_num :03d}.tex'
            else:
                test_file = f'{test_name}/{test_name}-{test_num :03d}.tex'
            with open(texFile, "r") as tex, open(templateFile, "r") as template, open(test_file, "w") as result:
                resultLines = []
                templateLines = template.readlines()
                templateLineCounter = 0
                while not templateLines[templateLineCounter].__contains__("<<exercises>>"):
                    resultLines.append(templateLines[templateLineCounter])
                    templateLineCounter += 1
                
                texLines = tex.readlines()
                foundBegin = False
                for line in texLines:
                    if line.__contains__("\\PyRopeExercise{"):
                        foundBegin = True
                    if line.__contains__("% Add a bibliography block to the postdoc"):
                        foundBegin = False
                        break
                    if foundBegin:
                        resultLines.append(line)
                
                templateLineCounter += 1
                while templateLineCounter < templateLines.__len__():
                    resultLines.append(templateLines[templateLineCounter])
                    templateLineCounter += 1
                
                result.writelines(resultLines)
                result.close()
            
        if test_num == 1:
            shutil.copytree('assets', test_name + '/assets')

    # try:
    #     os.remove(file)
    #     os.remove(texFile)
    # except FileNotFoundError:
    #     pass
