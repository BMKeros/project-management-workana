# -*- coding: utf-8 -*-
{
    'name': "project_managment_workana",

    'summary': """
        Modulo para la gestion de proyectos en grupo en la plataforma workana""",

    'description': """
        Modulo para la gestion de proyectos en grupo en la plataforma workana
    """,

    'author': "BMKeros",
    'website': "http://bmkeros.org.ve",

    'category': 'project',
    'version': '1.0',

    'depends': ['base'],

    'data': [
        'views/pm_workana_menu.xml',
        'views/pm_workana_project_view.xml',
        'views/pm_workana_distribution_line_view.xml',
        'views/pm_workana_deduction_line_view.xml',
    ],

    'demo': [
    ],
}