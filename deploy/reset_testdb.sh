mv fst_web/database/fst_demo.db db_bak.db
python manage.py makemigrations
python manage.py migrate
 python manage.py loaddata --settings=fst_web.settings fst_web/fs_doc/fixtures/exempeldata.json
cp fst_web/fs_doc/fixtures/allmanna_rad/*.pdf fst_web/uploads
cp fst_web/fs_doc/fixtures/foreskrift/*.pdf fst_web/uploads
cp fst_web/fs_doc/fixtures/bilaga/*.pdf fst_web/uploads
cp fst_web/fs_doc/fixtures/konsoliderad_foreskrift/*.pdf fst_web/uploads
python manage.py test
