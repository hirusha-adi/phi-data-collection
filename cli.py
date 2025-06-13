import click
from app import create_app, db
from app.models import User, Location, QuestionForm  # import your models
from flask import current_app
from flask.cli import with_appcontext

app = create_app()


@click.group()
def cli():
    """PHI App Management CLI"""
    pass


@cli.command("init-db")
@with_appcontext
def init_db():
    """Initialize the database (create tables)"""
    db.create_all()
    click.echo("✅ Initialized the database.")


@cli.command("drop-db")
@with_appcontext
def drop_db():
    """Drop all database tables"""
    if click.confirm("⚠️  This will delete all data. Are you sure?"):
        db.drop_all()
        click.echo("🗑️ Dropped all tables.")


@cli.command("seed-users")
@with_appcontext
def seed_users():
    """Seed the database with sample users"""
    from app.utils import create_default_users
    create_default_users()
    click.echo("👤 Default users created.")


@cli.command("delete-all-forms")
@with_appcontext
def delete_all_forms():
    """Delete all QuestionForm records"""
    num_deleted = QuestionForm.query.delete()
    db.session.commit()
    click.echo(f"🧹 Deleted {num_deleted} QuestionForm entries.")


@cli.command("add-sample-form")
@with_appcontext
def add_sample_form():
    """Add a sample form entry"""
    from datetime import datetime
    sample = QuestionForm(
        premises_registered=1,
        certificate_displayed=1,
        not_convicted=1,
        food_not_destroyed=1,
        safe_water=4,
        cleanliness=4,
        pests_animals=4,
        sound_pollution=4,
        toilets_cleanliness=4,
        medical_certificates=5,
        proper_clothing=5,
        unhygienic_behaviour=5,
        clean_utensils=5,
        walls_hygienic=4,
        floor_hygienic=4,
        ceiling_hygienic=4,
        food_surfaces_clean=4,
        wastewater_disposal=5,
        closed_bins=5,
        cooked_food_closed=4,
        cooked_food_temp=4,
        cooked_food_container=4,
        cooked_food_contam_prevented=4,
        uncooked_food_contam_prevented=4,
        location_id=1,  # make sure this exists
        user_id=1       # make sure this exists
    )
    db.session.add(sample)
    db.session.commit()
    click.echo("📄 Sample form added.")


if __name__ == '__main__':
    cli()
