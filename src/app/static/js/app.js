//inheriting ngMaterial from Google, and overlay.js

$(document).ready(function () {
});


(function () {
    'use strict';

    angular.module('scheduler', ['ngMaterial', 'ngDialog'])
        .controller('cNavigation', cNavigation)
        .controller('cSideCtrl', cSideCtrl);
		
	angular.module('scheduler').directive('cCourseBody',  function() { return {
		templateUrl: '/static/html/reccomendations.html'
	}});
	
	angular.module('scheduler').directive('cStudentBody',  function() { return {
		templateUrl: '/static/html/students.html'
	}});
	
	angular.module('scheduler').directive('cCalendarBody',  function() { return {
		templateUrl: '/static/html/calendar.html'
	}});

	angular.module('scheduler').directive('cSearch', function() { return {
		templateUrl: '/static/html/search.html',
		controllerAs: 'search',
		controller: function() {
			var self = this;
			self.searchTimeout = false;
			self.searchTree = function (searchString) {
            if (self.searchTimeout) {
                clearTimeout(self.searchTimeout);
            }
            self.searchTimeout = setTimeout(function () {
                $('#course_tree').jstree('search', searchString);
                //$('#course_tree').jstree(true).search(searchString);
            }, 300);
        };
		        self.clearSelected = function () {
            $('#schedule_tree').jstree(true).deselect_all();
        };
		
		}
	}});
	
		angular.module('scheduler').directive('cStudentSearch', function() { return {
		templateUrl: '/static/html/ssearch.html',
		controllerAs: 'ssearch',
		controller: function() {
			var self = this;
			self.searchTimeout = false;
			self.searchTree = function (searchString) {
            if (self.searchTimeout) {
                clearTimeout(self.searchTimeout);
            }
            self.searchTimeout = setTimeout(function () {
				$('#students_tree').jstree('ssearch', searchString);
            }, 300);
        };
		        self.clearSelected = function () {
            $('#schedule_tree').jstree(true).deselect_all();
        };
		
		}
	}});
	
		angular.module('scheduler').directive('cCourseInfo', function() { return {
		templateUrl: '/static/html/course_info.html',
		/**@ngInject**/controller: function(ngDialog) {
			$('#course_tree')
            .on('changed.jstree', function (e, data) {
                var i, j, r = [];
                for (i = 0, j = data.selected.length; i < j; i++) {
                    console.log('Pushing: ' + data.instance.get_node(data.selected[i]).text);
                    r.push(data.instance.get_node(data.selected[i]).text);
                }
                console.log('Selected: ' + r.join(', '));

                $.get("/api/courses/info", {
                    letter: data.node.a_attr['data-letter'],
                    number: data.node.a_attr['data-number']
                })
                    .done(function (data) {

                        console.log(data);
                        var dialog = ngDialog.open({
                            template: '<div>' +
                            '<h2>Course Info:</h2>' +
                            '<div><p><b>Name:</b> ' + data.name + '</p><p><b>Course Number: </b>' + data.letter + ' ' + data.number + '</p></div>' +
                            '<div><p><b>Credits:</b> ' + data.credits + '</p></div>' +
                            '<div><p><b>Description:</b> ' + data.details + '</p></div>' +
                            '<br />' +
                            '</div>',
                            className: 'ngdialog-theme-default',
                            plain: true, /*Change this to false for external templates */
                            showClose: false,
                            closeByDocument: true,
                            closeByEscape: true,
                            appendTo: false,
                        });
                    });


            })
            .jstree({
                'core': {
                    'data': function (obj, cb) {
                        $.get("/api/courses/tree", function (data) {
                            cb.call(this, data.results);
                        });
                    },
                    'themes': {
                        'icons': false
                    }
                },
                "search": {
                    "case_insensitive": true,
                    "show_only_matches": true,
                    "multiple": false
                },
                "plugins": ["search"]
            });
		}
	}});
	
	angular.module('scheduler').directive('cStudentInfo', function() { return {
		templateUrl: '/static/html/student_info.html',
		/**@ngInject**/controller: function(ngDialog) {
			$('#student_tree')
            .on('changed.jstree', function (e, data) {
                var i, j, r = [];
                for (i = 0, j = data.selected.length; i < j; i++) {
                    console.log('Pushing: ' + data.instance.get_node(data.selected[i]).text);
                    r.push(data.instance.get_node(data.selected[i]).text);
                }
                console.log('Selected: ' + r.join(', '));

                $.get("/api/students/info", {
                    name: data.node.a_attr['data-name']
                })
				.done(function (data) {

                        console.log(data);
                        var dialog = ngDialog.open({
                            template: '<div>' +
                            '<h2>Student Info:</h2>' +
                            '<div><p><b>Name:</b> ' + data.name + '</p><p><b>Campus Wide ID: </b>' + data.cwid  + '</p></div>' +
                            '<div><p><b>Courses Taken:</b> ' + data.courses + '</p></div>' +
                            '<br />' +
                            '</div>',
                            className: 'ngdialog-theme-default',
                            plain: true, /*Change this to false for external templates */
                            showClose: false,
                            closeByDocument: true,
                            closeByEscape: true,
                            appendTo: false,
                        });
                    });
            })
            .jstree({
                'core': {
                    'data': function (obj, cb) {
                        $.get("/api/students/tree", function (data) {
                            cb.call(this, data.results);
                        });
                    },
                    'themes': {
                        'icons': false
                   }
                },
                "ssearch": {
                    "case_insensitive": true,
                    "show_only_matches": true,
                    "multiple": false
                },
                "plugins": ["ssearch"]
            });
		}
	}});
	

    //tab module for optimal class selections
    function cTabModule($scope, $log, $rootScope) {
        $scope.tabs = [];
        $scope.selectedIndex = 0;
        $rootScope.selectedOption = 0;

        $scope.$watch('selectedIndex', function (current, old) {
            $rootScope.selectedOption = current - 1;
            $rootScope.$emit('onOptionChange');
        });

        $rootScope.$on('setTabCount', function (event, args) {
            $log.info('cTabModule.onEvent:' + args);
            $scope.tabs = [];
            for (var i = 0; i < parseInt(args); i++) {
                $scope.addTab('Option ' + (i + 1));
            }
            $scope.$apply();
        });

        $scope.addTab = function (title) {
            $log.info('title:' + title);
            $scope.tabs.push({title: title, disabled: false});
        };

        $scope.removeTab = function (tab) {
            var index = tabs.indexOf(tab);
            tabs.splice(index, 1);
        };

    }

    //Toggles side Navigation bar on and off
    function cNavigation($scope, $mdSidenav, $log) {
        $scope.toggleLeft = buildToggler('left');

        $scope.toggleLeft = function () {
            return $mdSidenav('left').toggle();
        };

        $scope.isSidebarOpen = function () {
            return $mdSidenav('left').isOpen();
        };

        function buildToggler(componentId) {
            return function () {
                $mdSidenav(componentId).toggle();
            }
        }
    }

    //Side control options Scheduler/Courses
    function cSideCtrl($scope, $log, $rootScope, ngDialog) {
        var self = this;
        self.nav = 'course_info';
		$rootScope.body = 'course_info';

        self.semesters = [
            {id: '2017S', name: 'Spring 2017'},
            {id: '2016F', name: 'Fall 2016'}
        ];

        self.selectedSemester = self.semesters[0];

        self.setSemester = function () {
            $log.info('setSemester:' + self.selectedSemester.name);
            $.get("/api/schedule/tree", {semester: self.selectedSemester.id}, function (data) {
                var tree = $('#schedule_tree');
                tree.jstree(true).settings.core.data = data.results;
                tree.jstree(true).uncheck_all();
                tree.jstree(true).refresh();
            });
        };

        self.setNav = function (page) {
            console.log("nav = " + page);
			console.log("body = " + page);
			$rootScope.body = page;
            self.nav = page;
			
        };
		
		$rootScope.getBody = function () {
            return $rootScope.body;
        };
	
        self.getNav = function () {
            return self.nav;
        };

        /**
         * Create filter function for a query string
         */
        function createFilterFor(query) {
            var lowercaseQuery = angular.lowercase(query);

            return function filterFn(item) {
                return (item.value.indexOf(lowercaseQuery) === 0) ||
                    (item.name.toLowerCase().indexOf(lowercaseQuery) === 0);
            };
        }
    }

})();
