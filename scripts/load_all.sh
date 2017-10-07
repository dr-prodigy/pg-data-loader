#!/usr/bin/env bash

#
# Copyright (c) 2017 Maurizio Montel.
#
# This file is part of the pg-data-loader distribution.
#   (https://github.com/dr-prodigy/pg-data-loader)
#
# FEEL is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, version 3.
#
# FEEL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# doc/info/contacts: https://github.com/dr-prodigy
#

cd ..
. venv/bin/activate
cd src
./loader.py ALL || exit
