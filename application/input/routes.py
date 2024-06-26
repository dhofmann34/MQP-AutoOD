import os
import time
from shutil import copyfile

import werkzeug.exceptions
from flask import render_template, request, flash, redirect, session, current_app
from werkzeug.utils import secure_filename
from application.input import input_bp
from application.input.input_processing import allowed_file, get_detection_methods, get_default_run_configuration, \
    call_autood_from_params
from connect import new_run
import json

results_global = None
final_log_filename_global = None


@input_bp.route('/autood/index', methods=['GET'])
def autood_form():
    return render_template('form.html')


@input_bp.route('/autood/index', methods=['POST'])
def autood_input():
    """Verifies the form input and return error messages if invalid.
    Checks if a pre-existing dataset has been selected. Runs AutoOD."""
    sample_file = None
    if 'selectedDataset' in request.form:
        sample_file = request.form['selectedDataset']
    if not sample_file:
        if 'file' not in request.files:
            flash('Please provide an input file or select a dataset.')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Please provide an input file or select a dataset.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('File type is not supported.')
            return redirect(request.url)
    else:
        filename = sample_file

    index_col_name = request.form['indexColName']
    label_col_name = request.form['labelColName']
    outlier_range_min = float(request.form['outlierRangeMin'])
    outlier_range_max = float(request.form['outlierRangeMax'])
    detection_methods = get_detection_methods(request.form.getlist('detectionMethods'))

    if not detection_methods:
        flash('Please choose at least one detection method.')
        return redirect(request.url)

    # Create dict for run configs
    run_configuration = {'index_col_name': index_col_name, 'label_col_name': label_col_name}
    run_configuration = get_default_run_configuration(run_configuration, detection_methods,
                                                      outlier_range_min, outlier_range_max)
    run_configuration['filename'] = filename

    results = call_autood_from_params(filename, run_configuration, detection_methods)

    if results.error_message:
        flash(results.error_message)
        return redirect(request.url)
    else:
        # Storing run results in the DB
        run_results = {'best_unsupervised_f1_score': results.best_unsupervised_f1_score,
                       'best_unsupervised_methods': results.best_unsupervised_methods,
                       'mv_f1_score': results.mv_f1_score,
                       'autood_f1_score': results.autood_f1_score}
        # Update the DB with the new run results
        user_id = session.get('user_id')
        new_run(user_id, json.dumps(run_configuration), json.dumps(run_results))
        return redirect('/autood/result')
