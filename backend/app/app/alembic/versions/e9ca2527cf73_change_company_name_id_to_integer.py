"""change company_name_id to integer

Revision ID: e9ca2527cf73
Revises: f831c5fb9525
Create Date: 2025-02-01 23:39:42.675556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e9ca2527cf73'
down_revision = 'f831c5fb9525'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop foreign key first
    op.execute('ALTER TABLE call_analysis_results DROP CONSTRAINT IF EXISTS call_analysis_results_company_name_id_fkey')
    
    # Create sequence for auto-incrementing company_name_id
    op.execute('CREATE SEQUENCE IF NOT EXISTS user_company_name_id_seq')
    
    # Change type in user table and set default from sequence
    op.execute('''
        ALTER TABLE "user" 
        ALTER COLUMN company_name_id TYPE INTEGER 
        USING COALESCE(company_name_id::integer, nextval('user_company_name_id_seq')),
        ALTER COLUMN company_name_id SET DEFAULT nextval('user_company_name_id_seq'),
        ALTER COLUMN company_name_id SET NOT NULL
    ''')
    
    # Change type in call_analysis_results table
    op.execute('''
        ALTER TABLE call_analysis_results 
        ALTER COLUMN company_name_id TYPE INTEGER 
        USING company_name_id::integer
    ''')
    
    # Recreate foreign key
    op.execute('''
        ALTER TABLE call_analysis_results 
        ADD CONSTRAINT call_analysis_results_company_name_id_fkey 
        FOREIGN KEY (company_name_id) 
        REFERENCES "user" (company_name_id)
    ''')
    
    # Изменяем типы float колонок
    op.alter_column('call_analysis_results', 'is_manager_established_contact',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_holding_initiative',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_using_dialog_programming',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_qualifying_client',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_identifying_pain',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_presenting_product',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_showing_expertise',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_handling_objections',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_setting_next_step',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_using_client_framing',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'final_grade',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=5),
               existing_nullable=False)

def downgrade() -> None:
    # Drop foreign key
    op.execute('ALTER TABLE call_analysis_results DROP CONSTRAINT IF EXISTS call_analysis_results_company_name_id_fkey')
    
    # Change type back in both tables
    op.execute('ALTER TABLE "user" ALTER COLUMN company_name_id TYPE VARCHAR USING company_name_id::varchar')
    op.execute('ALTER TABLE call_analysis_results ALTER COLUMN company_name_id TYPE VARCHAR USING company_name_id::varchar')
    
    # Drop sequence
    op.execute('DROP SEQUENCE IF EXISTS user_company_name_id_seq')
    
    # Recreate foreign key
    op.execute('''
        ALTER TABLE call_analysis_results 
        ADD CONSTRAINT call_analysis_results_company_name_id_fkey 
        FOREIGN KEY (company_name_id) 
        REFERENCES "user" (company_name_id)
    ''')
    
    # Возвращаем float колонки к REAL
    op.alter_column('call_analysis_results', 'final_grade',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_using_client_framing',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_setting_next_step',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_handling_objections',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_showing_expertise',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_presenting_product',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_identifying_pain',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_qualifying_client',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_using_dialog_programming',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_holding_initiative',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('call_analysis_results', 'is_manager_established_contact',
               existing_type=sa.Float(precision=10, decimal_return_scale=5),
               type_=sa.REAL(),
               existing_nullable=False)
