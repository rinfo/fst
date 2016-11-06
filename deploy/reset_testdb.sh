#!/usr/bin/env bash
rm -rf fst_web/uploads/*
mkdir fst_web/uploads/allmanna_rad/
mkdir fst_web/uploads/foreskrift/
mkdir fst_web/uploads/ovrigt/
mkdir fst_web/uploads/konsoliderad_foreskrift/
cp fst_web/fs_doc/fixtures/allmanna_rad/*.pdf fst_web/uploads/allmanna_rad/
cp fst_web/fs_doc/fixtures/foreskrift/*.pdf fst_web/uploads/foreskrift/
cp fst_web/fs_doc/fixtures/bilaga/*.pdf fst_web/uploads/ovrigt/
cp fst_web/fs_doc/fixtures/konsoliderad_foreskrift/*.pdf fst_web/uploads/konsoliderad_foreskrift/
cp fst_web/fs_doc/fixtures/demo-database/fst_demo.db fst_web/database/fst_demo.db
