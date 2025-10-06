from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
 op.create_table(
     "users",
     sa.Column("id", sa.Integer, primary_key=True),
     sa.Column("username", sa.String(50), unique=True, nullable=False),
     sa.Column("password_hash", sa.Text, nullable=False),
     sa.Column("role", sa.String(20), nullable=False),
     sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
     sa.Column("created_at", sa.TIMESTAMP, nullable=False, server_default=sa.text("NOW()")),
 )
 op.create_check_constraint("users_role_chk", "users", "role in ('admin','employee')")

 op.create_table(
     "bet_sets",
     sa.Column("id", sa.Integer, primary_key=True),
     sa.Column("name", sa.String(100), nullable=False, unique=True),
     sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
 )

 op.create_table(
     "bookmakers",
     sa.Column("id", sa.Integer, primary_key=True),
     sa.Column("name", sa.String(100), nullable=False, unique=True),
 )

 op.create_table(
     "bets",
     sa.Column("id", sa.BigInteger, primary_key=True),
     sa.Column("set_id", sa.Integer, sa.ForeignKey("bet_sets.id"), nullable=False),
     sa.Column("bookmaker_id", sa.Integer, sa.ForeignKey("bookmakers.id"), nullable=False),
     sa.Column("uploaded_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
     sa.Column("uploaded_at", sa.TIMESTAMP, nullable=False, server_default=sa.text("NOW()")),
     sa.Column("image_path", sa.Text, nullable=False),
     sa.Column("event_text", sa.Text),
     sa.Column("bet_type", sa.String(50)),
     sa.Column("odds_numeric", sa.Numeric(10,3)),
     sa.Column("stake_manual", sa.Numeric(12,2), nullable=False),
     sa.Column("potential_return", sa.Numeric(12,2)),
     sa.Column("cashout_amount", sa.Numeric(12,2)),
     sa.Column("commission_rate", sa.Numeric(5,4)),
     sa.Column("result_status", sa.String(20)),
     sa.Column("settled_at", sa.TIMESTAMP),
     sa.Column("profit", sa.Numeric(12,2), nullable=False, server_default="0"),
     sa.Column("raw_ocr_json", JSONB),
     sa.Column("parse_version", sa.Integer, nullable=False, server_default="1"),
     sa.Column("last_edited_by", sa.Integer, sa.ForeignKey("users.id")),
     sa.Column("last_edited_at", sa.TIMESTAMP),
 )

 op.create_table(
     "audit_log",
     sa.Column("id", sa.BigInteger, primary_key=True),
     sa.Column("bet_id", sa.BigInteger, sa.ForeignKey("bets.id", ondelete="SET NULL")),
     sa.Column("actor_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
     sa.Column("action", sa.String(40), nullable=False),
     sa.Column("before_json", JSONB),
     sa.Column("after_json", JSONB),
     sa.Column("created_at", sa.TIMESTAMP, nullable=False, server_default=sa.text("NOW()")),
 )

def downgrade():
 op.drop_table("audit_log")
 op.drop_table("bets")
 op.drop_table("bookmakers")
 op.drop_table("bet_sets")
 op.drop_table("users")