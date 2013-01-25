import sys

from cx_Freeze import setup, Executable

executable_target = Executable(
			script = "asdf.py",
			compress = True,
			icon = "icons/icon_asdf.png",
		)

includes = []
excludes = []
packages = []

setup(
        name = "asdf",
        version = "1.0",
		description = "asdf markdown editor.",
		author="Tsz-Ho Yu",
		author_email="thyu413@gmail.com",
		url="http://www.thyu.org",
		options = {"build_exe" : {
			"excludes" : excludes,
			"includes" : includes, 
			"packages": packages
			}
		},
        executables = [executable_target]
)

