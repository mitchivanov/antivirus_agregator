from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Threat, AntivirusProgram
import numpy as np


@app.route('/')
def index():
    threats = Threat.query.all()
    programs = AntivirusProgram.query.all()
    return render_template('index.html', threats=threats, programs=programs)


@app.route('/add_threat', methods=['GET', 'POST'])
def add_threat():
    if request.method == 'POST':
        name = request.form['name']
        damage = request.form['damage']
        description = request.form['description']

        if not name or not damage:
            flash('Название угрозы и ущерб обязательны к заполнению.', 'danger')
            return redirect(url_for('add_threat'))

        try:
            damage = float(damage)
        except ValueError:
            flash('Ущерб должен быть числом.', 'danger')
            return redirect(url_for('add_threat'))

        new_threat = Threat(name=name, damage=damage, description=description)
        db.session.add(new_threat)
        db.session.commit()

        for program in AntivirusProgram.query.all():
            efficacy_value = request.form.get(f'efficacy_{program.id}', 0)
            try:
                efficacy_value = float(efficacy_value)
            except ValueError:
                flash('Эффективность должна быть числом.', 'danger')
                return redirect(url_for('add_threat'))
            program.efficacy[name] = efficacy_value
            db.session.add(program)

        db.session.commit()
        flash('Угроза успешно добавлена.', 'success')
        return redirect(url_for('index'))

    programs = AntivirusProgram.query.all()
    return render_template('add_threat.html', programs=programs)


@app.route('/edit_threat/<int:id>', methods=['GET', 'POST'])
def edit_threat(id):
    threat = Threat.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        damage = request.form['damage']
        description = request.form['description']

        if not name or not damage:
            flash('Название угрозы и ущерб обязательны к заполнению.', 'danger')
            return redirect(url_for('edit_threat', id=id))

        try:
            damage = float(damage)
        except ValueError:
            flash('Ущерб должен быть числом.', 'danger')
            return redirect(url_for('edit_threat', id=id))

        threat.name = name
        threat.damage = damage
        threat.description = description
        db.session.commit()
        flash('Угроза успешно обновлена.', 'success')
        return redirect(url_for('index'))
    return render_template('edit_threat.html', threat=threat)


@app.route('/edit_program/<int:id>', methods=['GET', 'POST'])
def edit_program(id):
    program = AntivirusProgram.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        program_type = request.form['type']

        if not name or not price or not program_type:
            flash('Название программы, цена и тип обязательны к заполнению.', 'danger')
            return redirect(url_for('edit_program', id=id))

        try:
            price = float(price)
        except ValueError:
            flash('Цена должна быть числом.', 'danger')
            return redirect(url_for('edit_program', id=id))

        program.name = name
        program.price = price
        program.description = description
        program.type = program_type

        efficacy = program.efficacy.copy()
        for threat in Threat.query.all():
            efficacy_value = request.form.get(f'efficacy_{threat.id}', 0)
            try:
                efficacy_value = float(efficacy_value)
            except ValueError:
                flash('Эффективность должна быть числом.', 'danger')
                return redirect(url_for('edit_program', id=id))
            efficacy[threat.name] = efficacy_value

        program.efficacy = efficacy
        db.session.commit()
        flash('Программа успешно обновлена.', 'success')
        return redirect(url_for('index'))
    threats = Threat.query.all()
    return render_template('edit_program.html', program=program, threats=threats)


@app.route('/delete_threat/<int:id>')
def delete_threat(id):
    threat = Threat.query.get_or_404(id)
    db.session.delete(threat)
    db.session.commit()
    flash('Угроза успешно удалена.', 'success')
    return redirect(url_for('index'))


@app.route('/delete_program/<int:id>')
def delete_program(id):
    program = AntivirusProgram.query.get_or_404(id)
    db.session.delete(program)
    db.session.commit()
    flash('Программа успешно удалена.', 'success')
    return redirect(url_for('index'))


@app.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        program_type = request.form['type']

        if not name or not price or not program_type:
            flash('Название программы, цена и тип обязательны к заполнению.', 'danger')
            return redirect(url_for('add_program'))

        try:
            price = float(price)
        except ValueError:
            flash('Цена должна быть числом.', 'danger')
            return redirect(url_for('add_program'))

        efficacy = {}
        for threat in Threat.query.all():
            efficacy_value = request.form.get(f'efficacy_{threat.id}', 0)
            try:
                efficacy_value = float(efficacy_value)
            except ValueError:
                flash('Эффективность должна быть числом.', 'danger')
                return redirect(url_for('add_program'))
            efficacy[threat.name] = efficacy_value

        new_program = AntivirusProgram(name=name, price=price, efficacy=efficacy, description=description,
                                       type=program_type)
        db.session.add(new_program)
        db.session.commit()
        flash('Программа успешно добавлена.', 'success')
        return redirect(url_for('index'))

    threats = Threat.query.all()
    antivirus_programs = AntivirusProgram.query.filter_by(type='Антивирус').all()
    firewall_programs = AntivirusProgram.query.filter_by(type='Межсетевой экран').all()
    utility_programs = AntivirusProgram.query.filter_by(type='Антивирусная утилита').all()

    return render_template('add_program.html', threats=threats, antivirus_programs=antivirus_programs,
                           firewall_programs=firewall_programs, utility_programs=utility_programs)


@app.route('/results', methods=['POST'])
def results():
    selected_threats = request.form.getlist('threats')
    max_price = request.form['max_price']

    if not selected_threats:
        flash('Выберите хотя бы одну угрозу.', 'danger')
        return redirect(url_for('index'))

    if not max_price:
        flash('Введите максимальную цену.', 'danger')
        return redirect(url_for('index'))

    try:
        max_price = float(max_price)
    except ValueError:
        flash('Максимальная цена должна быть числом.', 'danger')
        return redirect(url_for('index'))

    threats = Threat.query.filter(Threat.id.in_(selected_threats)).all()
    programs = AntivirusProgram.query.all()

    if not threats or not programs:
        flash('Недостаточно данных для расчета.', 'danger')
        return redirect(url_for('index'))

    threats_data = [{'id': threat.id, 'name': threat.name, 'damage': threat.damage} for threat in threats]
    programs_data = [{'id': program.id, 'name': program.name, 'price': program.price, 'efficacy': program.efficacy,
                      'type': program.type} for program in programs]

    optimal_programs, reasons = calculate_optimal_programs_by_category(programs_data, threats_data)
    budget_programs, budget_reasons = calculate_optimal_programs_by_category_with_budget(programs_data, threats_data,
                                                                                         max_price)

    total_efficiency = calculate_total_efficiency(optimal_programs, threats_data)
    budget_total_efficiency = calculate_total_efficiency(budget_programs, threats_data)

    return render_template('results.html', optimal_programs=optimal_programs, reasons=reasons,
                           budget_programs=budget_programs, budget_reasons=budget_reasons,
                           total_efficiency=total_efficiency, budget_total_efficiency=budget_total_efficiency)


def calculate_optimal_programs_by_category(antivirus_programs, threats):
    categories = ['Антивирус', 'Межсетевой экран', 'Антивирусная утилита']
    optimal_programs = {}
    reasons = {}

    for category in categories:
        category_programs = [p for p in antivirus_programs if p['type'] == category]
        if not category_programs:
            optimal_programs[category] = None
            reasons[category] = ''
            continue

        num_programs = len(category_programs)
        num_threats = len(threats)

        efficacy_matrix = np.zeros((num_programs, num_threats))
        for i, program in enumerate(category_programs):
            for j, threat in enumerate(threats):
                efficacy_matrix[i, j] = program['efficacy'].get(threat['name'], 0)

        damage_vector = np.array([threat['damage'] for threat in threats])
        remaining_damages = np.dot((1 - efficacy_matrix), damage_vector)

        min_remaining_damage = np.min(remaining_damages)
        optimal_indices = np.where(remaining_damages == min_remaining_damage)[0]

        if min_remaining_damage >= np.sum(damage_vector):  # If all damages remain, it means no program is effective
            optimal_programs[category] = None
            reasons[category] = 'Нет подходящей программы'
            continue

        if len(optimal_indices) > 1:
            optimal_index = optimal_indices[np.argmin([category_programs[i]['price'] for i in optimal_indices])]
        else:
            optimal_index = optimal_indices[0]

        optimal_program = category_programs[optimal_index]
        protection_probability = 1 - (remaining_damages[optimal_index] / np.sum(damage_vector))
        reasons[category] = f'Эта программа выбрана, потому что она обеспечивает {protection_probability * 100:.2f}% защиту от атак.'

        optimal_programs[category] = optimal_program

    return optimal_programs, reasons



def calculate_optimal_programs_by_category_with_budget(antivirus_programs, threats, budget):
    categories = ['Антивирус', 'Межсетевой экран', 'Антивирусная утилита']
    optimal_programs = {}
    reasons = {}

    for category in categories:
        category_programs = [p for p in antivirus_programs if p['type'] == category]
        if not category_programs:
            optimal_programs[category] = None
            reasons[category] = ''
            continue

        num_programs = len(category_programs)
        num_threats = len(threats)

        efficacy_matrix = np.zeros((num_programs, num_threats))
        for i, program in enumerate(category_programs):
            for j, threat in enumerate(threats):
                efficacy_matrix[i, j] = program['efficacy'].get(threat['name'], 0)

        cost_vector = np.array([program['price'] for program in category_programs])
        damage_vector = np.array([threat['damage'] for threat in threats])
        remaining_damages = np.dot((1 - efficacy_matrix), damage_vector)

        feasible_indices = np.where(cost_vector <= budget)[0]
        if len(feasible_indices) == 0:
            optimal_programs[category] = None
            reasons[category] = 'Нет подходящей программы, которая вписывается в бюджет'
            continue

        feasible_remaining_damages = remaining_damages[feasible_indices]
        min_feasible_remaining_damage = np.min(feasible_remaining_damages)
        optimal_indices = np.where(feasible_remaining_damages == min_feasible_remaining_damage)[0]

        if min_feasible_remaining_damage >= np.sum(damage_vector):  # If all damages remain, it means no program is effective
            optimal_programs[category] = None
            reasons[category] = 'Нет подходящей программы, которая вписывается в бюджет'
            continue

        if len(optimal_indices) > 1:
            optimal_index = feasible_indices[optimal_indices[np.argmin([cost_vector[feasible_indices[i]] for i in optimal_indices])]]
        else:
            optimal_index = feasible_indices[optimal_indices[0]]

        optimal_program = category_programs[optimal_index]
        protection_probability = 1 - (feasible_remaining_damages[optimal_indices[0]] / np.sum(damage_vector))
        reasons[category] = f'Эта программа выбрана, потому что она обеспечивает {protection_probability * 100:.2f}% защиту от атак в пределах бюджета.'

        optimal_programs[category] = optimal_program

    return optimal_programs, reasons



def calculate_total_efficiency(programs, threats):
    total_efficiency = {threat['name']: 1.0 for threat in threats}
    for program in programs.values():
        if program:
            for threat in threats:
                total_efficiency[threat['name']] *= (1 - program['efficacy'].get(threat['name'], 0))

    # Конвертируем вероятность прохождения атак в вероятность защиты
    total_efficiency = {k: 1 - v for k, v in total_efficiency.items()}
    return total_efficiency
