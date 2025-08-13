# Makefile for building Waydroid SELinux policy modules

# SELinux policy development tools
SEMODULE = /usr/sbin/semodule
SEMODULE_PACKAGE = /usr/bin/semodule_package
CHECKMODULE = /usr/bin/checkmodule
SELINUX_MAKEFILE = /usr/share/selinux/devel/Makefile

# Policy modules
MODULES = waydroid waydroid_app waydroid_adbd

# Build targets
all: $(addsuffix .pp,$(MODULES))

%.pp: %.te %.fc
	@echo "Building $@ policy package"
	@if [ -f $(SELINUX_MAKEFILE) ]; then \
		make -f $(SELINUX_MAKEFILE) $@; \
	else \
		$(CHECKMODULE) -M -m -o $*.mod $*.te; \
		$(SEMODULE_PACKAGE) -o $@ -m $*.mod -f $*.fc; \
	fi

%.pp: %.te
	@echo "Building $@ policy package (no file contexts)"
	@if [ -f $(SELINUX_MAKEFILE) ]; then \
		make -f $(SELINUX_MAKEFILE) $@; \
	else \
		$(CHECKMODULE) -M -m -o $*.mod $*.te; \
		$(SEMODULE_PACKAGE) -o $@ -m $*.mod; \
	fi

install: all
	@echo "Installing SELinux policy modules"
	$(SEMODULE) -i $(addsuffix .pp,$(MODULES))

uninstall:
	@echo "Removing SELinux policy modules"
	-$(SEMODULE) -r $(MODULES)

load: all
	@echo "Loading SELinux policy modules"
	$(SEMODULE) -i $(addsuffix .pp,$(MODULES))

reload: all
	@echo "Reloading SELinux policy modules"
	$(SEMODULE) -r $(MODULES) 2>/dev/null || true
	$(SEMODULE) -i $(addsuffix .pp,$(MODULES))

clean:
	rm -f *.pp *.mod *.fc.tmp *.te.tmp

.PHONY: all install uninstall load reload clean