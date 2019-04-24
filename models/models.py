# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

DEDUCTION_AMOUNT = 'd_amount'
DEDUCTION_PERCENTAJE = 'd_percentaje'


class Project(models.Model):
    _name = "pm.workana.project"

    @api.onchange('distribution_line_ids')
    def _onchange_distribution_line_ids(self):
        total_percentaje = 0

        for distribution_line in self.distribution_line_ids:
            total_percentaje = total_percentaje + distribution_line.percentaje

        if total_percentaje > 100:
            raise ValidationError(
                'Las distribuciones superan el 100%% del proyecto')

    @api.onchange('deduction_line_ids')
    def _onchange_deduction_line_ids(self):
        self.calculate_profit_distribution()

    @api.multi
    @api.depends('amount', 'deduction_line_ids')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.amount

            for deduction_line in record.deduction_line_ids:
                if deduction_line.type.code == DEDUCTION_AMOUNT:
                    record.amount_total = record.amount_total - deduction_line.amount
                elif deduction_line.type.code == DEDUCTION_PERCENTAJE:
                    record.amount_total = record.amount_total - \
                        ((record.amount_total * deduction_line.amount)/100)

    @api.one
    def calculate_profit_distribution(self):
        for distribution_line in self.distribution_line_ids:
            distribution_line.profit = (
                (self.amount_total * distribution_line.percentaje) / 100)

    name = fields.Char(string="Project Name")
    amount = fields.Float(string="Project Amount")
    amount_total = fields.Float(
        string='Amount Total', compute='_compute_amount_total')
    date = fields.Date(string="Project Date")
    description = fields.Char(string='Project Description')

    distribution_line_ids = fields.Many2many('pm.workana.distribution.line',
                                             'pm_project_distribution_rel',
                                             'project_id',
                                             'distribution_line_id',
                                             string='Distribution',
                                             ondelete='cascade'
                                             )

    deduction_line_ids = fields.Many2many('pm.workana.deduction.line',
                                          'pm_project_deduction_rel',
                                          'project_id',
                                          'deduction_line_id',
                                          string='Deductions',
                                          ondelete='cascade'
                                          )

    @api.model
    def create(self, vals):
        print(vals)
        record = super(Project, self).create(vals)

        for distribution in record.distribution_line_ids:

            results = self.env['pm.workana.earning'].search([
                ['partner_id', '=', distribution.partner_id.id],
                ['project_id', '=', record.id]
            ])

            if len(results) == 0:
                self.env['pm.workana.earning'].create({
                    'partner_id': distribution.partner_id.id,
                    'project_id': record.id
                })

        return record


class DistributionLine(models.Model):
    _name = 'pm.workana.distribution.line'

    partner_id = fields.Many2one('res.partner', string='Colaborator')
    role_id = fields.Many2one('pm.workana.distribution.role', string='Role')
    percentaje = fields.Float(string='Percentaje')
    profit = fields.Float(string='Profit', compute='_compute_profit_amount')

    @api.one
    @api.depends('percentaje')
    def _compute_profit_amount(self):
        self.profit = ((self.env.context.get(
            'amount_total', 0) * self.percentaje) / 100)


class DistributionRole(models.Model):
    _name = 'pm.workana.distribution.role'
    _rec_name = 'title'

    title = fields.Char(string='Title')


class DeductionLine(models.Model):
    _name = 'pm.workana.deduction.line'
    _rec_name = 'type'

    type = fields.Many2one('pm.workana.deduction.type', string='Type')
    amount = fields.Float(string='Amount')
    description = fields.Char(string='Description')


class DeductionType(models.Model):
    _name = 'pm.workana.deduction.type'
    _rec_name = 'title'

    title = fields.Char(string='Title')
    code = fields.Selection(selection=[
        (DEDUCTION_AMOUNT, 'Amount'),
        (DEDUCTION_PERCENTAJE, 'Percentaje')
    ], string='Code')


class Earning(models.Model):
    _name = 'pm.workana.earning'

    project_id = fields.Many2one('pm.workana.project', string="Project")
    partner_id = fields.Many2one('res.partner', string="Colaborator")
    amount = fields.Float('Amount', compute="_compute_amount_total")

    @api.multi
    @api.depends('project_id', 'partner_id')
    def _compute_amount_total(self):
        for record in self:
            project = record.project_id
            total = 0

            for distribution in project.distribution_line_ids:
                if distribution.partner_id.id == record.partner_id.id:
                    total += (project.amount_total *
                              distribution.percentaje) / 100
            record.amount = total
